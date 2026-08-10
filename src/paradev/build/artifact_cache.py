"""Content-addressed finalized artifact-plan cache."""

from __future__ import annotations

import base64
import gzip
import hashlib
import io
import json
import logging
import os
import sys
import tempfile
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, replace
from functools import lru_cache
from importlib.metadata import PackageNotFoundError, version
from inspect import getsourcefile
from pathlib import Path
from typing import Literal, cast

from paradev.pdx import PDXBlock

from .artifacts import SpriteType
from .loaders import (
    CollectionSourceBundle,
    LocalizationEntry,
    ModuleSourceBundle,
)
from .plan import BuildContext
from .records import (
    Artifact,
    BuildResult,
    Collection,
    Dependency,
    Diagnostic,
    Module,
)
from .registry import BuildRegistry

ARTIFACT_PLAN_CACHE_SCHEMA = "paradev.artifact-plan-cache.v1"
_MAX_CACHE_BYTES = 256 * 1024 * 1024
_MAX_CACHE_JSON_BYTES = 768 * 1024 * 1024
_MAX_CACHE_RECORDS = 250_000
_CACHE_CODE_PATHS = (
    Path(__file__),
    Path(__file__).with_name("artifacts.py"),
    Path(__file__).with_name("families.py"),
    Path(__file__).with_name("plan.py"),
    Path(__file__).with_name("records.py"),
    Path(__file__).with_name("registry.py"),
    Path(__file__).parent.parent / "pdx" / "ast.py",
    Path(__file__).parent.parent / "portable_paths.py",
    Path(__file__).parent.parent / "sdk" / "project.py",
)

ArtifactPlanCacheStatus = Literal["hit", "miss", "refresh", "bypass"]
logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class CachedArtifactPlan:
    """One finalized build plan and its cache disposition."""

    result: BuildResult
    status: ArtifactPlanCacheStatus
    signature: str | None = None


def artifact_plan_signature(
    *,
    project_id: str,
    profile: str | None,
    metadata: Mapping[str, object],
    module_cache_signature: str,
    collection_cache_signature: str,
    copy_artifacts: Sequence[Artifact],
    copy_diagnostics: Sequence[Diagnostic],
    registry: BuildRegistry,
) -> str | None:
    """Return the complete signature, or ``None`` when reuse is not proven."""

    context = BuildContext(
        project_id=project_id,
        metadata=dict(metadata),
    )
    postprocessor_keys: list[dict[str, object]] = []
    for postprocessor in registry.postprocessors:
        cache_key = getattr(postprocessor, "artifact_cache_key", None)
        if not callable(cache_key):
            return None
        try:
            value = cache_key(context)
            _json_bytes(value)
        except Exception as error:
            logger.warning(
                "Artifact plan caching is disabled because postprocessor %s could not fingerprint its external inputs (%s: %s).",
                type(postprocessor).__qualname__,
                type(error).__name__,
                error,
            )
            return None
        if value is None:
            return None
        postprocessor_keys.append(
            {
                "postprocessor": _component_identity(
                    "postprocessor",
                    postprocessor,
                ),
                "key": value,
            }
        )

    payload = {
        "schema": ARTIFACT_PLAN_CACHE_SCHEMA,
        "engine": _cache_engine_fingerprint(),
        "project_id": project_id,
        "profile": profile,
        "metadata": dict(metadata),
        "module_cache": module_cache_signature,
        "collection_cache": collection_cache_signature,
        "copy_artifacts": [artifact.to_dict() for artifact in copy_artifacts],
        "copy_diagnostics": [item.to_dict() for item in copy_diagnostics],
        "registry": registry.to_view(),
        "postprocessor_keys": postprocessor_keys,
        "components": [_component_identity("family", item) for item in registry.families]
        + [_component_identity("writer", item) for item in registry.writers]
        + [_component_identity("postprocessor", item) for item in registry.postprocessors],
    }
    return _json_digest(payload)


def cached_artifact_plan(
    cache_root: Path,
    *,
    project_id: str,
    project_root: Path,
    profile: str | None,
    emit_artifacts: bool,
    signature: str | Callable[[], str | None],
    source_modules: Sequence[Module],
    source_collections: Sequence[Collection],
    read: bool,
    write: bool,
    builder: Callable[[], BuildResult],
) -> CachedArtifactPlan:
    """Load or rebuild one finalized project artifact plan."""

    identity = {
        "project_id": project_id,
        "project_root": str(project_root.resolve()),
        "profile": profile,
        "emit_artifacts": emit_artifacts,
    }
    path = _cache_path(cache_root, identity)
    before = _resolved_signature(signature)
    if before is None:
        return CachedArtifactPlan(result=builder(), status="bypass")
    status: ArtifactPlanCacheStatus = "bypass" if not read else "miss"
    if read:
        cache_exists = path.exists()
        document = _read_cache(path)
        if document is not None:
            if document.get("schema") == ARTIFACT_PLAN_CACHE_SCHEMA and document.get("identity") == identity and document.get("signature") == before:
                payload = document.get("payload")
                payload_digest = document.get("payload_sha256")
                if isinstance(payload, Mapping) and payload_digest == _json_digest(payload):
                    try:
                        result = _decode_result(
                            cast(Mapping[str, object], payload),
                            project_id=project_id,
                            profile=profile,
                            source_modules=source_modules,
                            source_collections=source_collections,
                        )
                    except Exception as error:
                        logger.warning(
                            "Ignoring invalid artifact plan cache %s; the plan will be rebuilt (%s: %s).",
                            path,
                            type(error).__name__,
                            error,
                        )
                        status = "refresh"
                    else:
                        return CachedArtifactPlan(
                            result=result,
                            status="hit",
                            signature=before,
                        )
                else:
                    status = "refresh"
            else:
                status = "refresh"
        elif cache_exists:
            status = "refresh"

    result = builder()
    after = _resolved_signature(signature)
    if after is None:
        return CachedArtifactPlan(result=result, status="bypass")
    if after != before:
        status = "refresh"
        before = after
        result = builder()
        after = _resolved_signature(signature)
        if after is None:
            return CachedArtifactPlan(result=result, status="bypass")
        if after != before:
            raise RuntimeError("Artifact plan inputs changed repeatedly while planning. " "Wait for the external edit to finish and retry the build.")
    if write:
        try:
            payload = _encode_result(result)
            _write_cache(
                path,
                {
                    "schema": ARTIFACT_PLAN_CACHE_SCHEMA,
                    "identity": identity,
                    "signature": after,
                    "payload_sha256": _json_digest(payload),
                    "payload": payload,
                },
            )
        except Exception as error:
            logger.warning(
                "Could not write artifact plan cache %s; this build remains valid but later builds may replan (%s: %s).",
                path,
                type(error).__name__,
                error,
            )
    return CachedArtifactPlan(
        result=result,
        status=status,
        signature=after,
    )


def _resolved_signature(
    signature: str | Callable[[], str | None],
) -> str | None:
    value = signature() if callable(signature) else signature
    if value is None:
        return None
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError("Artifact plan cache signature must be one SHA-256 digest.")
    return value


def _cache_path(cache_root: Path, identity: Mapping[str, object]) -> Path:
    return cache_root / f"{_json_digest(identity)}.json.gz"


def _component_identity(kind: str, component: object) -> dict[str, str]:
    component_type = type(component)
    source = getsourcefile(component_type) or ""
    source_digest = ""
    path = Path(source)
    if path.is_file():
        try:
            source_digest = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError:
            source_digest = "unreadable"
    return {
        "kind": kind,
        "module": component_type.__module__,
        "qualname": component_type.__qualname__,
        "source": source,
        "source_sha256": source_digest,
    }


@lru_cache(maxsize=1)
def _cache_engine_fingerprint() -> str:
    digest = hashlib.sha256()
    runtime = {
        "schema": ARTIFACT_PLAN_CACHE_SCHEMA,
        "python": f"{sys.version_info.major}.{sys.version_info.minor}",
        "paradev": _package_version("paradev"),
        "heavenbase": _package_version("heavenbase"),
        "pyyaml": _package_version("PyYAML"),
    }
    digest.update(_json_bytes(runtime))
    for path in sorted(_CACHE_CODE_PATHS, key=str):
        try:
            payload = path.read_bytes()
        except OSError:
            continue
        digest.update(str(path).encode("utf-8"))
        digest.update(hashlib.sha256(payload).digest())
    return digest.hexdigest()


def _package_version(package: str) -> str:
    try:
        return version(package)
    except PackageNotFoundError:
        return "uninstalled"


def _read_cache(path: Path) -> dict[str, object] | None:
    try:
        if path.stat().st_size > _MAX_CACHE_BYTES:
            return None
        compressed = path.read_bytes()
        with gzip.GzipFile(fileobj=io.BytesIO(compressed), mode="rb") as stream:
            payload = stream.read(_MAX_CACHE_JSON_BYTES + 1)
        if len(payload) > _MAX_CACHE_JSON_BYTES:
            return None
        document = json.loads(payload)
    except (EOFError, OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    return document if isinstance(document, dict) else None


def _write_cache(path: Path, document: Mapping[str, object]) -> None:
    payload = _json_bytes(document)
    if len(payload) > _MAX_CACHE_JSON_BYTES:
        raise ValueError("Artifact plan cache entry exceeds the safe JSON size limit.")
    compressed = gzip.compress(payload, compresslevel=1, mtime=0)
    if len(compressed) > _MAX_CACHE_BYTES:
        raise ValueError("Artifact plan cache entry exceeds the safe file size limit.")
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix=f".{path.name}.",
            suffix=".tmp",
            dir=path.parent,
            delete=False,
        ) as handle:
            temp_path = Path(handle.name)
            handle.write(compressed)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


def _encode_result(result: BuildResult) -> dict[str, object]:
    return {
        "project_id": result.project_id,
        "profile": result.profile,
        "dry_run": result.dry_run,
        "modules": [_encode_module(item) for item in result.modules],
        "collections": [_encode_collection(item) for item in result.collections],
        "dependencies": [_encode_dependency(item) for item in result.dependencies],
        "artifacts": [_encode_artifact(item) for item in result.artifacts],
        "diagnostics": [_encode_diagnostic(item) for item in result.diagnostics],
    }


def _decode_result(
    payload: Mapping[str, object],
    *,
    project_id: str,
    profile: str | None,
    source_modules: Sequence[Module],
    source_collections: Sequence[Collection],
) -> BuildResult:
    if _text(payload.get("project_id"), "project_id") != project_id:
        raise ValueError("Cached artifact plan project id does not match its owner.")
    cached_profile = _optional_text(payload.get("profile"), "profile")
    if cached_profile != profile:
        raise ValueError("Cached artifact plan profile does not match its owner.")
    if payload.get("dry_run") is not True:
        raise ValueError("Cached artifact plans must be dry-run results.")
    cached_modules = tuple(_decode_module(item) for item in _mapping_sequence(payload.get("modules"), "modules"))
    cached_collections = tuple(_decode_collection(item) for item in _mapping_sequence(payload.get("collections"), "collections"))
    modules = _rehydrated_modules(cached_modules, source_modules)
    collections = _rehydrated_collections(
        cached_collections,
        source_collections,
    )
    dependencies = tuple(_decode_dependency(item) for item in _mapping_sequence(payload.get("dependencies"), "dependencies"))
    artifacts = tuple(_decode_artifact(item) for item in _mapping_sequence(payload.get("artifacts"), "artifacts"))
    diagnostics = tuple(_decode_diagnostic(item) for item in _mapping_sequence(payload.get("diagnostics"), "diagnostics"))
    for name, rows in (
        ("modules", modules),
        ("collections", collections),
        ("dependencies", dependencies),
        ("artifacts", artifacts),
        ("diagnostics", diagnostics),
    ):
        if len(rows) > _MAX_CACHE_RECORDS:
            raise ValueError(f"Cached artifact plan contains too many {name}.")
    result = BuildResult(
        project_id=project_id,
        profile=profile,
        modules=modules,
        collections=collections,
        dependencies=dependencies,
        artifacts=artifacts,
        diagnostics=diagnostics,
        dry_run=True,
    )
    validation = BuildResult.plan(
        project_id,
        profile=profile,
        modules=modules,
        collections=collections,
        artifacts=artifacts,
    )
    if validation.modules != modules:
        raise ValueError("Cached artifact plan module order is invalid.")
    if validation.collections != collections:
        raise ValueError("Cached artifact plan collections are invalid.")
    if validation.dependencies != dependencies:
        raise ValueError("Cached artifact plan dependencies are invalid.")
    cached_diagnostics = {_diagnostic_key(item) for item in diagnostics}
    if any(_diagnostic_key(item) not in cached_diagnostics for item in validation.diagnostics):
        raise ValueError("Cached artifact plan fails generic build validation.")
    return result


def _encode_module(module: Module) -> dict[str, object]:
    if module.payload is not None and not isinstance(
        module.payload,
        ModuleSourceBundle,
    ):
        raise TypeError(f"Module payload type {type(module.payload).__module__}.{type(module.payload).__qualname__} is not cacheable.")
    return {
        "module_id": module.module_id,
        "family": module.family,
        "root": str(module.root),
        "source_slots": _encode_source_slots(module.source_slots),
        "collection_id": module.collection_id,
        "metadata": dict(module.metadata),
    }


def _decode_module(payload: Mapping[str, object]) -> Module:
    return Module(
        module_id=_text(payload.get("module_id"), "module_id"),
        family=_text(payload.get("family"), "family"),
        root=_text(payload.get("root"), "root"),
        source_slots=_decode_source_slots(payload.get("source_slots")),
        collection_id=_optional_text(payload.get("collection_id"), "collection_id"),
        metadata=dict(_mapping(payload.get("metadata"), "metadata")),
    )


def _encode_collection(collection: Collection) -> dict[str, object]:
    if collection.payload is not None and not isinstance(
        collection.payload,
        CollectionSourceBundle,
    ):
        raise TypeError(f"Collection payload type {type(collection.payload).__module__}.{type(collection.payload).__qualname__} is not cacheable.")
    return {
        "collection_id": collection.collection_id,
        "family": collection.family,
        "module_ids": list(collection.module_ids),
        "source_slots": _encode_source_slots(collection.source_slots),
        "metadata": dict(collection.metadata),
    }


def _decode_collection(payload: Mapping[str, object]) -> Collection:
    return Collection(
        collection_id=_text(payload.get("collection_id"), "collection_id"),
        family=_text(payload.get("family"), "family"),
        module_ids=_text_sequence(payload.get("module_ids"), "module_ids"),
        source_slots=_decode_source_slots(payload.get("source_slots")),
        metadata=dict(_mapping(payload.get("metadata"), "metadata")),
    )


def _rehydrated_modules(
    cached: Sequence[Module],
    source: Sequence[Module],
) -> tuple[Module, ...]:
    source_by_id = {module.module_id: module for module in source}
    hydrated: list[Module] = []
    for module in cached:
        source_module = source_by_id.get(module.module_id)
        payload = source_module.payload if source_module is not None else None
        if isinstance(payload, ModuleSourceBundle):
            payload = replace(payload, metadata=dict(module.metadata))
        hydrated.append(replace(module, payload=payload))
    return tuple(hydrated)


def _rehydrated_collections(
    cached: Sequence[Collection],
    source: Sequence[Collection],
) -> tuple[Collection, ...]:
    source_by_id = {(collection.family, collection.collection_id): collection for collection in source}
    hydrated: list[Collection] = []
    for collection in cached:
        source_collection = source_by_id.get((collection.family, collection.collection_id))
        payload = source_collection.payload if source_collection is not None else None
        if isinstance(payload, CollectionSourceBundle):
            payload = replace(payload, metadata=dict(collection.metadata))
        hydrated.append(replace(collection, payload=payload))
    return tuple(hydrated)


def _encode_dependency(dependency: Dependency) -> dict[str, object]:
    return dependency.to_dict()


def _decode_dependency(payload: Mapping[str, object]) -> Dependency:
    return Dependency(
        source=_text(payload.get("source"), "source"),
        target=_text(payload.get("target"), "target"),
        kind=_text(payload.get("kind"), "kind"),
        metadata=dict(_mapping(payload.get("metadata", {}), "metadata")),
    )


def _encode_artifact(artifact: Artifact) -> dict[str, object]:
    return {
        "path": str(artifact.path),
        "artifact_type": artifact.artifact_type,
        "owner": artifact.owner,
        "inputs": [str(path) for path in artifact.inputs],
        "mode": artifact.mode,
        "target_root": artifact.target_root,
        "metadata": dict(artifact.metadata),
        "payload": _encode_artifact_payload(artifact.payload),
    }


def _decode_artifact(payload: Mapping[str, object]) -> Artifact:
    return Artifact(
        path=_text(payload.get("path"), "path"),
        artifact_type=_text(payload.get("artifact_type"), "artifact_type"),
        owner=_text(payload.get("owner"), "owner"),
        inputs=_text_sequence(payload.get("inputs"), "inputs"),
        mode=_text(payload.get("mode"), "mode"),
        target_root=_text(payload.get("target_root"), "target_root"),
        metadata=dict(_mapping(payload.get("metadata"), "metadata")),
        payload=_decode_artifact_payload(_mapping(payload.get("payload"), "payload")),
    )


def _encode_artifact_payload(payload: object) -> dict[str, object]:
    if payload is None:
        return {"kind": "none"}
    if isinstance(payload, PDXBlock):
        return {"kind": "pdx_text", "value": payload.to_str()}
    if isinstance(payload, bytes):
        return {
            "kind": "bytes",
            "value": base64.b64encode(payload).decode("ascii"),
        }
    if isinstance(payload, str):
        return {"kind": "text", "value": payload}
    if isinstance(payload, tuple) and all(isinstance(item, SpriteType) for item in payload):
        return {
            "kind": "sprites",
            "value": [
                {
                    "name": item.name,
                    "texturefile": item.texturefile,
                    "properties": dict(item.properties),
                }
                for item in payload
            ],
        }
    if isinstance(payload, tuple) and all(isinstance(item, LocalizationEntry) for item in payload):
        return {
            "kind": "localization",
            "value": [
                {
                    "key": item.key,
                    "language": item.language,
                    "text": item.text,
                    "source_path": item.source_path,
                    "module_id": item.module_id,
                }
                for item in payload
            ],
        }
    if isinstance(payload, (bool, int, float, list, dict)):
        _json_bytes(payload)
        return {"kind": "json", "value": payload}
    raise TypeError(f"Artifact payload type {type(payload).__module__}.{type(payload).__qualname__} is not cacheable.")


def _decode_artifact_payload(payload: Mapping[str, object]) -> object:
    kind = _text(payload.get("kind"), "payload.kind")
    if kind == "none":
        return None
    if kind == "pdx_text":
        return _text(payload.get("value"), "payload.value", allow_empty=True)
    if kind == "bytes":
        value = _text(payload.get("value"), "payload.value", allow_empty=True)
        return base64.b64decode(value.encode("ascii"), validate=True)
    if kind == "text":
        return _text(payload.get("value"), "payload.value", allow_empty=True)
    if kind == "sprites":
        return tuple(
            SpriteType(
                name=_text(item.get("name"), "sprite.name"),
                texturefile=_text(item.get("texturefile"), "sprite.texturefile"),
                properties=dict(_mapping(item.get("properties"), "sprite.properties")),
            )
            for item in _mapping_sequence(payload.get("value"), "payload.value")
        )
    if kind == "localization":
        return tuple(
            LocalizationEntry(
                key=_text(item.get("key"), "localization.key"),
                language=_text(item.get("language"), "localization.language"),
                text=_text(
                    item.get("text"),
                    "localization.text",
                    allow_empty=True,
                ),
                source_path=_text(
                    item.get("source_path"),
                    "localization.source_path",
                ),
                module_id=_optional_text(
                    item.get("module_id"),
                    "localization.module_id",
                ),
            )
            for item in _mapping_sequence(payload.get("value"), "payload.value")
        )
    if kind == "json":
        value = payload.get("value")
        _json_bytes(value)
        return value
    raise ValueError(f"Unknown cached artifact payload kind: {kind!r}.")


def _encode_diagnostic(diagnostic: Diagnostic) -> dict[str, object]:
    return diagnostic.to_dict()


def _decode_diagnostic(payload: Mapping[str, object]) -> Diagnostic:
    span_value = payload.get("span")
    span = None
    if span_value is not None:
        span = {str(key): _integer(value, f"span.{key}") for key, value in _mapping(span_value, "span").items()}
    return Diagnostic(
        code=_text(payload.get("code"), "code"),
        message=_text(payload.get("message"), "message", allow_empty=True),
        severity=_text(payload.get("severity"), "severity"),
        family=_optional_text(payload.get("family"), "family"),
        module_id=_optional_text(payload.get("module_id"), "module_id"),
        collection_id=_optional_text(
            payload.get("collection_id"),
            "collection_id",
        ),
        slot=_optional_text(payload.get("slot"), "slot"),
        source_path=_optional_text(payload.get("source_path"), "source_path"),
        artifact_path=_optional_text(
            payload.get("artifact_path"),
            "artifact_path",
        ),
        target_root=_optional_text(payload.get("target_root"), "target_root"),
        span=span,
        slots=_text_sequence(payload.get("slots", ()), "slots"),
        owners=_text_sequence(payload.get("owners", ()), "owners"),
    )


def _diagnostic_key(diagnostic: Diagnostic) -> str:
    return _json_digest(diagnostic.to_dict())


def _encode_source_slots(
    source_slots: Mapping[str, Sequence[str | Path]],
) -> dict[str, list[str]]:
    return {str(slot): [str(path) for path in paths] for slot, paths in sorted(source_slots.items())}


def _decode_source_slots(value: object) -> dict[str, tuple[str, ...]]:
    return {str(slot): _text_sequence(paths, f"source_slots.{slot}") for slot, paths in _mapping(value, "source_slots").items()}


def _json_digest(value: object) -> str:
    return hashlib.sha256(_json_bytes(value)).hexdigest()


def _json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _mapping(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} must be a mapping.")
    return cast(Mapping[str, object], value)


def _mapping_sequence(
    value: object,
    name: str,
) -> tuple[Mapping[str, object], ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise TypeError(f"{name} must be a sequence.")
    return tuple(_mapping(item, f"{name}[]") for item in value)


def _text(value: object, name: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str) or (not allow_empty and not value):
        raise TypeError(f"{name} must be a string.")
    return value


def _optional_text(value: object, name: str) -> str | None:
    if value is None:
        return None
    return _text(value, name)


def _text_sequence(value: object, name: str) -> tuple[str, ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise TypeError(f"{name} must be a sequence.")
    return tuple(_text(item, f"{name}[]") for item in value)


def _integer(value: object, name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{name} must be an integer.")
    return value


__all__ = [
    "ARTIFACT_PLAN_CACHE_SCHEMA",
    "ArtifactPlanCacheStatus",
    "CachedArtifactPlan",
    "artifact_plan_signature",
    "cached_artifact_plan",
]
