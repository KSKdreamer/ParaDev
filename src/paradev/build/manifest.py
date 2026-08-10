"""Build manifest payload and file helpers."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import stat
import tempfile
from collections.abc import Mapping
from functools import lru_cache
from pathlib import Path
from typing import Any

from heavenbase.utils import dumps_json

from paradev._api_table import append_index_entry, append_nested_index_entry

from ._fs import AnchoredDirectory, open_anchored_directory
from .artifacts import SpriteType
from .loaders import CollectionSourceBundle, DEFAULT_COPY_SLOTS, DEFAULT_LOC_SLOTS, DEFAULT_PDX_SLOTS, ModuleSourceBundle
from .records import BuildResult, Collection, Diagnostic, Module

MANIFEST_SCHEMAS = {
    "modules.json": "paradev.build.modules.v1",
    "collections.json": "paradev.build.collections.v1",
    "dependencies.json": "paradev.build.dependencies.v1",
    "artifacts.json": "paradev.build.artifacts.v1",
    "assets.json": "paradev.build.assets.v1",
    "diagnostics.json": "paradev.build.diagnostics.v1",
    "localization.json": "paradev.build.localization.v1",
    "sources.json": "paradev.build.sources.v1",
    "source-map.json": "paradev.build.source-map.v1",
    "sprites.json": "paradev.build.sprites.v1",
    "summary.json": "paradev.build.summary.v1",
}
MANIFEST_PUBLICATION_CACHE_SCHEMA = "paradev.manifest-publication-cache.v1"
_MAX_MANIFEST_CACHE_BYTES = 256 * 1024
_MANIFEST_CACHE_CODE_PATHS = (
    Path(__file__),
    Path(__file__).parent.parent / "_api_table.py",
)
logger = logging.getLogger(__name__)


def manifest_payloads(result: BuildResult) -> dict[str, dict[str, Any]]:
    """Return stable manifest payloads for a build result."""

    assets = _assets(result)
    artifacts = [artifact.to_dict() for artifact in result.artifacts]
    collections = [collection.to_dict() for collection in result.collections]
    modules = [module.to_dict() for module in result.modules]
    dependencies = [dependency.to_dict() for dependency in result.dependencies]
    diagnostics = _diagnostics(result)
    localization = _localization(result)
    sources = _sources(result)
    source_map = _source_map(result)
    sprites = _sprites(result)
    return {
        "modules.json": _payload(result, "modules.json", {"modules": modules, "index": module_index(modules)}),
        "collections.json": _payload(result, "collections.json", {"collections": collections, "index": collection_index(collections)}),
        "dependencies.json": _payload(
            result,
            "dependencies.json",
            {"dependencies": dependencies, "index": dependency_index(dependencies)},
        ),
        "artifacts.json": _payload(result, "artifacts.json", {"artifacts": artifacts, "index": artifact_index(artifacts)}),
        "assets.json": _payload(result, "assets.json", {"assets": assets, "index": asset_index(assets)}),
        "diagnostics.json": _payload(
            result,
            "diagnostics.json",
            {
                "diagnostics": diagnostics,
                "index": diagnostic_index(diagnostics),
                "family_index": diagnostic_family_index(diagnostics),
            },
        ),
        "localization.json": _payload(result, "localization.json", {"localization": localization, "index": localization_index(localization)}),
        "sources.json": _payload(result, "sources.json", {"sources": sources, "index": source_inventory_index(sources)}),
        "source-map.json": _payload(result, "source-map.json", {"source_map": source_map, "index": source_map_index(source_map)}),
        "sprites.json": _payload(result, "sprites.json", {"sprites": sprites, "index": sprite_index(sprites)}),
        "summary.json": _summary_payload(result),
    }


def manifest_rows(result: BuildResult, manifest_name: str) -> list[dict[str, Any]]:
    """Build only one manifest's data rows without materializing all manifests.

    Args:
        result: Build result to project.
        manifest_name: Supported manifest filename whose primary rows should
            be returned.

    Returns:
        Fresh JSON-safe rows without the manifest envelope or lookup indexes.

    Raises:
        ValueError: If ``manifest_name`` has no row-only projection.
    """

    if manifest_name == "dependencies.json":
        return [dependency.to_dict() for dependency in result.dependencies]
    builders = {
        "assets.json": _assets,
        "diagnostics.json": _diagnostics,
        "localization.json": _localization,
        "source-map.json": _source_map,
        "sources.json": _sources,
        "sprites.json": _sprites,
    }
    builder = builders.get(manifest_name)
    if builder is None:
        raise ValueError(f"Unsupported row-only manifest: {manifest_name!r}.")
    return [dict(row) for row in builder(result)]


def localization_index(rows: object) -> dict[str, dict[str, dict[str, object]]]:
    """Return deterministic language/key lookup metadata for localization rows."""

    row_indexes: dict[tuple[str, str], list[int]] = {}
    duplicates: dict[tuple[str, str], bool] = {}
    for row_index, row in enumerate(rows if isinstance(rows, list) else ()):
        if not isinstance(row, dict):
            continue
        language = row.get("language")
        key = row.get("key")
        if not isinstance(language, str) or not isinstance(key, str):
            continue
        index_key = (language, key)
        append_index_entry(row_indexes, index_key, row_index)
        duplicates[index_key] = duplicates.get(index_key, False) or bool(row.get("duplicate"))

    languages = sorted({language for language, _key in row_indexes})
    return {
        language: {
            key: {"duplicate": duplicates[(language, key)], "rows": row_indexes[(language, key)]}
            for key in sorted(key for row_language, key in row_indexes if row_language == language)
        }
        for language in languages
    }


def module_index(rows: object) -> dict[str, dict[str, list[int]]]:
    """Return deterministic id, family, collection, and slot lookup metadata for modules."""

    index: dict[str, dict[str, list[int]]] = {"id": {}, "family": {}, "collection": {}, "slot": {}}
    for row_index, row in enumerate(rows if isinstance(rows, list) else ()):
        if not isinstance(row, dict):
            continue
        _append_row_index(index["id"], row.get("module_id"), row_index)
        _append_row_index(index["family"], row.get("family"), row_index)
        _append_row_index(index["collection"], row.get("collection_id"), row_index)
        slots = row.get("source_slots")
        for slot in sorted(slots) if isinstance(slots, dict) else ():
            _append_row_index(index["slot"], slot, row_index)
    return {name: {key: bucket[key] for key in sorted(bucket)} for name, bucket in index.items() if bucket}


def collection_index(rows: object) -> dict[str, dict[str, list[int]]]:
    """Return deterministic id, family, member-module, and slot lookup metadata for collections."""

    index: dict[str, dict[str, list[int]]] = {"id": {}, "family": {}, "module": {}, "slot": {}}
    for row_index, row in enumerate(rows if isinstance(rows, list) else ()):
        if not isinstance(row, dict):
            continue
        _append_row_index(index["id"], row.get("collection_id"), row_index)
        _append_row_index(index["family"], row.get("family"), row_index)
        module_ids = row.get("module_ids")
        for module_id in sorted(module_ids) if isinstance(module_ids, list) else ():
            _append_row_index(index["module"], module_id, row_index)
        slots = row.get("source_slots")
        for slot in sorted(slots) if isinstance(slots, dict) else ():
            _append_row_index(index["slot"], slot, row_index)
    return {name: {key: bucket[key] for key in sorted(bucket)} for name, bucket in index.items() if bucket}


def artifact_index(rows: object) -> dict[str, dict[str, list[int]]]:
    """Return deterministic artifact lookup metadata."""

    index: dict[str, dict[str, list[int]]] = {
        "path": {},
        "type": {},
        "owner": {},
        "target_root": {},
        "mode": {},
        "module": {},
        "collection": {},
    }
    for row_index, row in enumerate(rows if isinstance(rows, list) else ()):
        if not isinstance(row, dict):
            continue
        for key in ("path", "type", "owner", "target_root", "mode"):
            _append_row_index(index[key], row.get(key), row_index)
        for module_id in artifact_module_ids(row):
            _append_row_index(index["module"], module_id, row_index)
        for collection_id in artifact_collection_ids(row):
            _append_row_index(index["collection"], collection_id, row_index)
    return {name: {key: bucket[key] for key in sorted(bucket)} for name, bucket in index.items() if bucket}


def artifact_module_ids(row: object) -> tuple[str, ...]:
    """Return module ids directly owning or contributing to an artifact row."""

    if not isinstance(row, Mapping):
        return ()
    module_ids: set[str] = set()
    _add_owner_id(module_ids, row.get("owner"), "module")
    _add_text(module_ids, row.get("module_id"))
    metadata = row.get("metadata")
    if isinstance(metadata, Mapping):
        _add_text(module_ids, metadata.get("module_id"))
        _add_texts(module_ids, metadata.get("module_ids"))
        nodes = metadata.get("nodes")
        for node in nodes if isinstance(nodes, list) else ():
            if isinstance(node, Mapping):
                _add_text(module_ids, node.get("module_id"))
    sources = row.get("sources")
    for source in sources if isinstance(sources, list) else ():
        if isinstance(source, Mapping):
            _add_text(module_ids, source.get("module_id"))
    return tuple(sorted(module_ids))


def artifact_collection_ids(row: object) -> tuple[str, ...]:
    """Return collection ids directly owning or contributing to an artifact row."""

    if not isinstance(row, Mapping):
        return ()
    collection_ids: set[str] = set()
    _add_owner_id(collection_ids, row.get("owner"), "collection")
    _add_text(collection_ids, row.get("collection_id"))
    metadata = row.get("metadata")
    if isinstance(metadata, Mapping):
        _add_text(collection_ids, metadata.get("collection_id"))
        _add_texts(collection_ids, metadata.get("collection_ids"))
    sources = row.get("sources")
    for source in sources if isinstance(sources, list) else ():
        if isinstance(source, Mapping):
            _add_text(collection_ids, source.get("collection_id"))
    return tuple(sorted(collection_ids))


def _append_row_index(bucket: dict[str, list[int]], value: object, row_index: int) -> None:
    if isinstance(value, str) and value:
        append_index_entry(bucket, value, row_index)


def _add_owner_id(bucket: set[str], owner: object, owner_type: str) -> None:
    prefix = f"{owner_type}:"
    if isinstance(owner, str) and owner.startswith(prefix):
        _add_text(bucket, owner.removeprefix(prefix))


def _add_text(bucket: set[str], value: object) -> None:
    if isinstance(value, str) and value:
        bucket.add(value)


def _add_texts(bucket: set[str], values: object) -> None:
    for value in values if isinstance(values, list) else ():
        _add_text(bucket, value)


def dependency_index(rows: object) -> dict[str, dict[str, list[int]]]:
    """Return deterministic source/kind lookup metadata for dependency rows."""

    index: dict[str, dict[str, list[int]]] = {}
    for row_index, row in enumerate(rows if isinstance(rows, list) else ()):
        if not isinstance(row, dict):
            continue
        source = row.get("source")
        kind = row.get("kind")
        if not isinstance(source, str) or not isinstance(kind, str):
            continue
        append_nested_index_entry(index, source, kind, row_index)
    return {source: {kind: kinds[kind] for kind in sorted(kinds)} for source, kinds in sorted(index.items())}


def source_inventory_index(rows: object) -> dict[str, dict[str, list[int]]]:
    """Return deterministic owner/slot lookup metadata for source rows."""

    index: dict[str, dict[str, list[int]]] = {}
    for row_index, row in enumerate(rows if isinstance(rows, list) else ()):
        if not isinstance(row, dict):
            continue
        owner_id = row.get("module_id")
        if not isinstance(owner_id, str):
            owner_id = row.get("collection_id")
        slot = row.get("slot")
        if not isinstance(owner_id, str) or not isinstance(slot, str):
            continue
        append_nested_index_entry(index, owner_id, slot, row_index)
    return {owner_id: {slot: slots[slot] for slot in sorted(slots)} for owner_id, slots in sorted(index.items())}


def write_manifests(result: BuildResult, build_root: str | Path) -> dict[str, Path]:
    """Write build manifest JSON files under a build root.

    Args:
        result: Build result to serialize.
        build_root: Target `.paradev/.cache/build` directory.

    Returns:
        Mapping from manifest file name to written path.
    """

    with open_anchored_directory(Path(build_root)) as publication_root:
        return _write_manifests_anchored(result, publication_root)


def _write_manifests_anchored(
    result: BuildResult,
    publication_root: AnchoredDirectory,
    *,
    cache_path: Path | None = None,
    plan_signature: str | None = None,
) -> dict[str, Path]:
    """Write build manifests through a retained publication authority."""

    if (cache_path is None) != (plan_signature is None):
        raise ValueError("Manifest publication reuse requires both a cache path and artifact-plan signature.")
    cache_key = _manifest_publication_cache_key(plan_signature) if plan_signature is not None else None
    if cache_path is not None and cache_key is not None:
        cached_digests = _read_manifest_publication_cache(cache_path, cache_key=cache_key)
        if cached_digests is not None and all(
            publication_root.file_sha256_matches(name, cached_digests[name]) is True for name in MANIFEST_SCHEMAS
        ):
            return {name: publication_root.requested_path / name for name in MANIFEST_SCHEMAS}

    written: dict[str, Path] = {}
    manifest_digests: dict[str, str] = {}
    for name, payload in manifest_payloads(result).items():
        encoded = dumps_json(
            payload,
            sort_keys=True,
            compact=True,
            adapt=False,
        ).encode("utf-8")
        digest = hashlib.sha256(encoded).hexdigest()
        manifest_digests[name] = digest
        if publication_root.file_sha256_matches(name, digest) is True:
            written[name] = publication_root.requested_path / name
            continue
        written[name] = publication_root.write_bytes(name, encoded)
    if cache_path is not None and cache_key is not None:
        try:
            _write_manifest_publication_cache(
                cache_path,
                cache_key=cache_key,
                manifest_digests=manifest_digests,
            )
        except Exception as error:
            logger.warning(
                "Could not write manifest publication cache %s; this build remains valid but later builds may regenerate manifests (%s: %s).",
                cache_path,
                type(error).__name__,
                error,
            )
    return written


def _manifest_publication_cache_key(plan_signature: str) -> str:
    """Bind one manifest receipt to exact plan and projection implementations."""

    if not _is_sha256(plan_signature):
        raise ValueError("Manifest publication reuse requires one SHA-256 artifact-plan signature.")
    return hashlib.sha256(
        _manifest_cache_json_bytes(
            {
                "schema": MANIFEST_PUBLICATION_CACHE_SCHEMA,
                "engine": _manifest_cache_engine_fingerprint(),
                "plan_signature": plan_signature,
                "manifest_schemas": MANIFEST_SCHEMAS,
            }
        )
    ).hexdigest()


@lru_cache(maxsize=1)
def _manifest_cache_engine_fingerprint() -> str:
    digest = hashlib.sha256()
    for path in _MANIFEST_CACHE_CODE_PATHS:
        try:
            payload = path.read_bytes()
        except OSError:
            digest.update(f"unreadable:{path.name}".encode("utf-8"))
            continue
        digest.update(path.name.encode("utf-8"))
        digest.update(hashlib.sha256(payload).digest())
    return digest.hexdigest()


def _read_manifest_publication_cache(
    path: Path,
    *,
    cache_key: str,
) -> dict[str, str] | None:
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return None
    except OSError as error:
        logger.warning(
            "Could not inspect manifest publication cache %s; manifests will be regenerated (%s: %s).",
            path,
            type(error).__name__,
            error,
        )
        return None
    try:
        if not stat.S_ISREG(metadata.st_mode):
            raise ValueError("cache path is not a regular file")
        if metadata.st_size > _MAX_MANIFEST_CACHE_BYTES:
            raise ValueError("cache file exceeds the safe size limit")
        document = json.loads(path.read_bytes())
        if not isinstance(document, Mapping) or document.get("schema") != MANIFEST_PUBLICATION_CACHE_SCHEMA:
            raise ValueError("cache envelope has an unsupported schema")
        payload = document.get("payload")
        if not isinstance(payload, Mapping) or document.get("payload_sha256") != hashlib.sha256(_manifest_cache_json_bytes(payload)).hexdigest():
            raise ValueError("cache payload checksum is invalid")
        if payload.get("cache_key") != cache_key:
            return None
        digests = payload.get("manifests")
        if not isinstance(digests, Mapping) or set(digests) != set(MANIFEST_SCHEMAS):
            raise ValueError("cache manifest inventory is invalid")
        result = {str(name): str(digest) for name, digest in digests.items()}
        if any(not _is_sha256(digest) for digest in result.values()):
            raise ValueError("cache contains an invalid manifest digest")
        return result
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError) as error:
        logger.warning(
            "Ignoring invalid manifest publication cache %s; manifests will be regenerated (%s: %s).",
            path,
            type(error).__name__,
            error,
        )
        return None


def _write_manifest_publication_cache(
    path: Path,
    *,
    cache_key: str,
    manifest_digests: Mapping[str, str],
) -> None:
    if set(manifest_digests) != set(MANIFEST_SCHEMAS) or any(not _is_sha256(digest) for digest in manifest_digests.values()):
        raise ValueError("Manifest publication cache requires the complete exact digest inventory.")
    payload = {
        "cache_key": cache_key,
        "manifests": {name: manifest_digests[name] for name in MANIFEST_SCHEMAS},
    }
    document = {
        "schema": MANIFEST_PUBLICATION_CACHE_SCHEMA,
        "payload_sha256": hashlib.sha256(_manifest_cache_json_bytes(payload)).hexdigest(),
        "payload": payload,
    }
    encoded = _manifest_cache_json_bytes(document)
    if len(encoded) > _MAX_MANIFEST_CACHE_BYTES:
        raise ValueError("Manifest publication cache exceeds the safe size limit.")
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
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


def _manifest_cache_json_bytes(value: object) -> bytes:
    return dumps_json(
        value,
        sort_keys=True,
        compact=True,
        adapt=False,
    ).encode("utf-8")


def _is_sha256(value: object) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    try:
        bytes.fromhex(value)
    except ValueError:
        return False
    return True


def _summary_payload(result: BuildResult) -> dict[str, Any]:
    """Build only the compact summary manifest payload."""

    return _payload(result, "summary.json", {"summary": result.summary()})


def _payload(result: BuildResult, name: str, data: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema": MANIFEST_SCHEMAS[name],
        "project_id": result.project_id,
    }
    if result.profile:
        payload["profile"] = result.profile
    payload.update(data)
    return payload


def _source_map(result: BuildResult) -> list[dict[str, Any]]:
    source_index = _source_index(result)
    rows: list[dict[str, Any]] = []
    for artifact in result.artifacts:
        inputs = [_path_text(path) for path in artifact.inputs]
        rows.append(
            {
                "artifact_path": _path_text(artifact.path),
                "type": artifact.artifact_type,
                "target_root": artifact.target_root,
                "owner": artifact.owner,
                "inputs": inputs,
                "sources": [source for input_path in inputs for source in _input_sources(input_path, source_index)],
            }
        )
    return rows


def _sources(result: BuildResult) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for module in result.modules:
        rows.extend(_module_source_rows(result, module))
    for collection in result.collections:
        rows.extend(_collection_source_rows(result, collection))
    return sorted(rows, key=_source_row_key)


def _module_source_rows(result: BuildResult, module: Module) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    bundle = module.payload if isinstance(module.payload, ModuleSourceBundle) else None
    root = Path(module.root)
    for slot in sorted(module.source_slots):
        for source_path in sorted(module.source_slots[slot]):
            rel_path = _path_text(source_path)
            path = _path_text(root / rel_path)
            row = {
                "owner_kind": "module",
                "module_id": module.module_id,
                "family": module.family,
                "root": _path_text(root),
                "slot": slot,
                "path": path,
                "relative_path": rel_path,
            }
            _add_source_details(row, bundle, slot, rel_path)
            _add_source_diagnostics(result, row)
            rows.append(row)
    return rows


def _collection_source_rows(result: BuildResult, collection: Collection) -> list[dict[str, Any]]:
    payload = collection.payload
    if not isinstance(payload, CollectionSourceBundle):
        return []
    root = Path(payload.root)
    rows: list[dict[str, Any]] = []
    for slot in sorted(payload.source_slots):
        for source_path in sorted(payload.source_slots[slot]):
            rel_path = _path_text(source_path)
            path = _path_text(root / rel_path)
            row = {
                "owner_kind": "collection",
                "collection_id": collection.collection_id,
                "family": collection.family,
                "root": _path_text(root),
                "slot": slot,
                "path": path,
                "relative_path": rel_path,
            }
            _add_collection_source_details(row, payload, slot, rel_path)
            _add_source_diagnostics(result, row)
            rows.append(row)
    return rows


def _add_source_details(row: dict[str, Any], bundle: ModuleSourceBundle | None, slot: str, rel_path: str) -> None:
    if bundle is not None and _add_bundle_source_details(row, bundle.pdx_sources, bundle.loc_entries, bundle.copy_sources, rel_path):
        return
    row.update({"loader": _matched_source_loader(slot), "status": "matched"})


def _add_collection_source_details(row: dict[str, Any], bundle: CollectionSourceBundle, slot: str, rel_path: str) -> None:
    if _add_bundle_source_details(row, bundle.pdx_sources, bundle.loc_entries, bundle.copy_sources, rel_path):
        return
    row.update({"loader": _matched_source_loader(slot), "status": "matched"})


def _add_bundle_source_details(
    row: dict[str, Any],
    pdx_sources: object,
    loc_entries: object,
    copy_sources: object,
    rel_path: str,
) -> bool:
    for source in pdx_sources if isinstance(pdx_sources, tuple) else ():
        if _path_text(source.path) == rel_path:
            row.update({"loader": "pdx", "status": "loaded", "entry_count": len(source.block.entries)})
            return True
    loc_entry_rows = loc_entries if isinstance(loc_entries, tuple) else ()
    source_loc_entries = [entry for entry in loc_entry_rows if _path_text(entry.source_path) == rel_path]
    if source_loc_entries:
        row.update(
            {
                "loader": "loc",
                "status": "loaded",
                "localization_count": len(source_loc_entries),
                "languages": sorted({entry.language for entry in source_loc_entries}),
            }
        )
        return True
    for source in copy_sources if isinstance(copy_sources, tuple) else ():
        if _path_text(source.path) == rel_path:
            _add_copy_source_details(row, source.to_dict())
            return True
    return False


def _add_copy_source_details(row: dict[str, Any], source: Mapping[str, object]) -> None:
    row.update({"loader": "copy", "status": "loaded"})
    for key in ("output_path", "sha256", "content_sha256", "media_type", "format"):
        value = source.get(key)
        if isinstance(value, str) and value:
            row[key] = value
    for key in ("size", "width", "height"):
        value = source.get(key)
        if type(value) is int:
            row[key] = value


def _add_source_diagnostics(result: BuildResult, row: dict[str, Any]) -> None:
    codes = _source_diagnostic_codes(result, row)
    if codes:
        row["diagnostic_codes"] = codes
        if row.get("status") != "loaded":
            row["status"] = "diagnostic"


def _source_diagnostic_codes(result: BuildResult, row: Mapping[str, Any]) -> list[str]:
    owner_kind = row.get("owner_kind")
    module_id = row.get("module_id")
    collection_id = row.get("collection_id")
    slot = row.get("slot")
    rel_path = row.get("relative_path")
    path = row.get("path")
    codes: list[str] = []
    for diagnostic in result.diagnostics:
        if owner_kind == "module" and diagnostic.module_id != module_id:
            continue
        if owner_kind == "collection" and diagnostic.collection_id != collection_id:
            continue
        if diagnostic.slot and diagnostic.slot != slot:
            continue
        if diagnostic.source_path is None and diagnostic.slot is None:
            continue
        if diagnostic.source_path is None:
            codes.append(diagnostic.code)
            continue
        source_path = _path_text(diagnostic.source_path)
        if source_path not in {rel_path, path}:
            continue
        codes.append(diagnostic.code)
    return sorted(dict.fromkeys(codes))


def _matched_source_loader(slot: str) -> str:
    if slot in DEFAULT_PDX_SLOTS:
        return "pdx"
    if slot in DEFAULT_LOC_SLOTS:
        return "loc"
    if slot in DEFAULT_COPY_SLOTS:
        return "copy"
    return "unknown"


def _source_row_key(row: Mapping[str, Any]) -> tuple[str, str, str, str, str]:
    owner_id = row.get("module_id")
    if not isinstance(owner_id, str):
        owner_id = row.get("collection_id")
    return (
        str(row.get("owner_kind") or ""),
        owner_id if isinstance(owner_id, str) else "",
        str(row.get("slot") or ""),
        str(row.get("relative_path") or ""),
        str(row.get("path") or ""),
    )


def _assets(result: BuildResult) -> list[dict[str, Any]]:
    source_index = _source_index(result)
    rows: list[dict[str, Any]] = []
    for artifact in result.artifacts:
        if artifact.artifact_type != "copy":
            continue
        metadata = artifact.metadata if isinstance(artifact.metadata, Mapping) else {}
        inputs = [_path_text(path) for path in artifact.inputs]
        source = _copy_artifact_source(inputs, source_index)
        row: dict[str, Any] = {}
        for key in ("module_id", "collection_id", "family", "slot"):
            value = source.get(key)
            if value:
                row[key] = value
        source_path = _metadata_text(metadata, "path")
        if source_path:
            row["source_path"] = source_path
        row["artifact_path"] = _path_text(artifact.path)
        row["owner"] = artifact.owner
        row["target_root"] = artifact.target_root
        for key in ("sha256", "media_type", "format"):
            value = _metadata_text(metadata, key)
            if value:
                row[key] = value
        for key in ("size", "width", "height"):
            value = _metadata_int(metadata, key)
            if value is not None:
                row[key] = value
        if source:
            row["source"] = source
        rows.append(row)
    return rows


def asset_index(rows: object) -> dict[str, dict[str, list[int]]]:
    """Return deterministic owner/slot lookup metadata for asset rows."""

    return _owner_slot_index(rows)


def sprite_index(rows: object) -> dict[str, dict[str, list[int]]]:
    """Return deterministic owner/slot lookup metadata for sprite rows."""

    return _owner_slot_index(rows)


def _owner_slot_index(rows: object) -> dict[str, dict[str, list[int]]]:
    index: dict[str, dict[str, list[int]]] = {}
    for row_index, row in enumerate(rows if isinstance(rows, list) else ()):
        if not isinstance(row, dict):
            continue
        owner_id = row.get("module_id")
        if not isinstance(owner_id, str):
            owner_id = row.get("collection_id")
        slot = row.get("slot")
        if not isinstance(owner_id, str) or not isinstance(slot, str):
            continue
        append_nested_index_entry(index, owner_id, slot, row_index)
    return {owner_id: {slot: slots[slot] for slot in sorted(slots)} for owner_id, slots in sorted(index.items())}


def _sprites(result: BuildResult) -> list[dict[str, Any]]:
    source_index = _source_index(result)
    rows: list[dict[str, Any]] = []
    for artifact in result.artifacts:
        if artifact.artifact_type != "sprite_gfx":
            continue
        metadata = artifact.metadata if isinstance(artifact.metadata, Mapping) else {}
        family = _metadata_text(metadata, "family")
        inputs = [_path_text(path) for path in artifact.inputs]
        for index, sprite in enumerate(_sprite_payload(artifact.payload)):
            input_path = inputs[index] if index < len(inputs) else None
            source = dict(_input_sources(input_path, source_index)[0]) if input_path else {}
            row: dict[str, Any] = {
                "name": sprite.name,
                "texturefile": sprite.texturefile,
                "artifact_path": _path_text(artifact.path),
                "owner": artifact.owner,
                "target_root": artifact.target_root,
            }
            if family:
                row["family"] = family
            for key in ("module_id", "collection_id", "slot"):
                value = source.get(key)
                if value:
                    row[key] = value
            if "family" not in row and source.get("family"):
                row["family"] = source["family"]
            if input_path:
                row["source_path"] = input_path
            if sprite.properties:
                row["properties"] = dict(sorted(sprite.properties.items()))
            if source:
                row["source"] = source
            rows.append(row)
    return rows


def _sprite_payload(payload: object) -> tuple[SpriteType, ...]:
    if not isinstance(payload, tuple):
        return ()
    return tuple(sprite for sprite in payload if isinstance(sprite, SpriteType))


def diagnostic_index(rows: object) -> dict[str, dict[str, list[int]]]:
    """Return deterministic severity/code lookup metadata for diagnostic rows."""

    index: dict[str, dict[str, list[int]]] = {}
    for row_index, row in enumerate(rows if isinstance(rows, list) else ()):
        if not isinstance(row, dict):
            continue
        severity = row.get("severity")
        code = row.get("code")
        if not isinstance(severity, str) or not isinstance(code, str):
            continue
        append_nested_index_entry(index, severity, code, row_index)
    return {severity: {code: codes[code] for code in sorted(codes)} for severity, codes in sorted(index.items())}


def diagnostic_family_index(rows: object) -> dict[str, dict[str, dict[str, list[int]]]]:
    """Return deterministic family/severity/code lookup metadata for diagnostics."""

    index: dict[str, dict[str, dict[str, list[int]]]] = {}
    for row_index, row in enumerate(rows if isinstance(rows, list) else ()):
        if not isinstance(row, dict):
            continue
        family = _diagnostic_family(row)
        severity = row.get("severity")
        code = row.get("code")
        if not isinstance(family, str) or not isinstance(severity, str) or not isinstance(code, str):
            continue
        append_nested_index_entry(index.setdefault(family, {}), severity, code, row_index)
    return {
        family: {severity: {code: codes[code] for code in sorted(codes)} for severity, codes in sorted(severities.items())}
        for family, severities in sorted(index.items())
    }


def _diagnostic_family(row: dict[str, Any]) -> str | None:
    family = row.get("family")
    if isinstance(family, str):
        return family
    source = row.get("source")
    if isinstance(source, dict):
        family = source.get("family")
        if isinstance(family, str):
            return family
    return None


def source_map_index(rows: object) -> dict[str, dict[str, list[int]]]:
    """Return deterministic owner/slot lookup metadata for source-map rows."""

    index: dict[str, dict[str, list[int]]] = {}
    for row_index, row in enumerate(rows if isinstance(rows, list) else ()):
        if not isinstance(row, dict):
            continue
        sources = row.get("sources")
        seen: set[tuple[str, str]] = set()
        for source in sources if isinstance(sources, list) else ():
            if not isinstance(source, dict):
                continue
            owner_id = source.get("module_id")
            if not isinstance(owner_id, str):
                owner_id = source.get("collection_id")
            slot = source.get("slot")
            if not isinstance(owner_id, str) or not isinstance(slot, str):
                continue
            key = (owner_id, slot)
            if key in seen:
                continue
            seen.add(key)
            append_nested_index_entry(index, owner_id, slot, row_index)
    return {owner_id: {slot: slots[slot] for slot in sorted(slots)} for owner_id, slots in sorted(index.items())}


def _copy_artifact_source(
    inputs: list[str],
    source_index: dict[str, tuple[dict[str, str], ...]],
) -> dict[str, str]:
    if not inputs:
        return {}
    return dict(_input_sources(inputs[0], source_index)[0])


def _diagnostics(result: BuildResult) -> list[dict[str, Any]]:
    module_map = {module.module_id: module for module in result.modules}
    collection_map = {collection.collection_id: collection for collection in result.collections}
    source_index = _source_index(result)
    rows: list[dict[str, Any]] = []
    for diagnostic in result.diagnostics:
        row = diagnostic.to_dict()
        source = _diagnostic_source(diagnostic, module_map, collection_map, source_index)
        if source:
            row["source"] = source
        rows.append(row)
    return rows


def _localization(result: BuildResult) -> list[dict[str, Any]]:
    source_index = _source_index(result)
    entry_rows = [
        ("module", module, entry) for module in result.modules if isinstance(module.payload, ModuleSourceBundle) for entry in module.payload.loc_entries
    ]
    entry_rows.extend(
        ("collection", collection, entry)
        for collection in result.collections
        if isinstance(collection.payload, CollectionSourceBundle)
        for entry in collection.payload.loc_entries
    )
    duplicate_counts: dict[tuple[str, str], int] = {}
    for _kind, _owner, entry in entry_rows:
        duplicate_key = (entry.language, entry.key)
        duplicate_counts[duplicate_key] = duplicate_counts.get(duplicate_key, 0) + 1

    rows: list[dict[str, Any]] = []
    for kind, owner, entry in sorted(
        entry_rows,
        key=lambda row: (_localization_owner_id(row[0], row[1]), row[2].language, row[2].key, row[2].source_path, row[2].text),
    ):
        duplicate = duplicate_counts[(entry.language, entry.key)] > 1
        if kind == "module" and isinstance(owner, Module):
            rows.append(
                {
                    "module_id": owner.module_id,
                    "family": owner.family,
                    "language": entry.language,
                    "key": entry.key,
                    "text": entry.text,
                    "source_path": _path_text(entry.source_path),
                    "duplicate": duplicate,
                    "source": _module_localization_source(owner, entry.source_path, source_index),
                }
            )
        elif kind == "collection" and isinstance(owner, Collection):
            rows.append(
                {
                    "collection_id": owner.collection_id,
                    "family": owner.family,
                    "language": entry.language,
                    "key": entry.key,
                    "text": entry.text,
                    "source_path": _path_text(entry.source_path),
                    "duplicate": duplicate,
                    "source": _collection_localization_source(owner, entry.source_path, source_index),
                }
            )
    return rows


def _source_index(result: BuildResult) -> dict[str, tuple[dict[str, str], ...]]:
    source_map: dict[str, list[dict[str, str]]] = {}
    for module in result.modules:
        root = Path(module.root)
        for slot in sorted(module.source_slots):
            for source_path in module.source_slots[slot]:
                path = _path_text(root / source_path)
                append_index_entry(
                    source_map,
                    path,
                    {
                        "path": path,
                        "module_id": module.module_id,
                        "family": module.family,
                        "slot": slot,
                    },
                )
    for collection in result.collections:
        payload = collection.payload
        if not isinstance(payload, CollectionSourceBundle):
            continue
        root = Path(payload.root)
        for source in payload.pdx_sources:
            path = _path_text(root / source.path)
            _append_source(
                source_map,
                path,
                {
                    "path": path,
                    "collection_id": collection.collection_id,
                    "family": collection.family,
                    "slot": source.slot,
                },
            )
        for entry in payload.loc_entries:
            path = _path_text(root / entry.source_path)
            _append_source(
                source_map,
                path,
                {
                    "path": path,
                    "collection_id": collection.collection_id,
                    "family": collection.family,
                    "slot": _collection_source_slot(collection, entry.source_path) or "loc",
                },
            )
        for source in payload.copy_sources:
            path = _path_text(root / source.path)
            _append_source(
                source_map,
                path,
                {
                    "path": path,
                    "collection_id": collection.collection_id,
                    "family": collection.family,
                    "slot": source.slot,
                },
            )
    return {path: tuple(sources) for path, sources in source_map.items()}


def _append_source(source_map: dict[str, list[dict[str, str]]], path: str, source: dict[str, str]) -> None:
    rows = source_map.setdefault(path, [])
    if source not in rows:
        rows.append(source)


def _input_sources(input_path: str, source_index: dict[str, tuple[dict[str, str], ...]]) -> tuple[dict[str, str], ...]:
    sources = source_index.get(input_path)
    if sources:
        return sources
    return ({"path": input_path},)


def _diagnostic_source(
    diagnostic: Diagnostic,
    module_map: dict[str, Module],
    collection_map: dict[str, Collection],
    source_index: dict[str, tuple[dict[str, str], ...]],
) -> dict[str, str] | None:
    if diagnostic.source_path is None:
        return None
    source_path = _path_text(diagnostic.source_path)
    module = module_map.get(diagnostic.module_id or "")
    collection = collection_map.get(diagnostic.collection_id or "")
    candidate_paths = [source_path]
    if module:
        candidate_paths.insert(0, _path_text(Path(module.root) / source_path))
    elif collection and isinstance(collection.payload, CollectionSourceBundle):
        candidate_paths.insert(0, _path_text(Path(collection.payload.root) / source_path))

    for path in candidate_paths:
        sources = source_index.get(path)
        if not sources:
            continue
        if diagnostic.slot:
            for source in sources:
                if source.get("slot") == diagnostic.slot:
                    return dict(source)
        return dict(sources[0])

    if module:
        source = {"path": candidate_paths[0], "module_id": module.module_id, "family": module.family}
        if diagnostic.slot:
            source["slot"] = diagnostic.slot
        return source
    if collection:
        source = {"path": candidate_paths[0], "collection_id": collection.collection_id, "family": collection.family}
        if diagnostic.slot:
            source["slot"] = diagnostic.slot
        return source
    return {"path": source_path}


def _module_localization_source(
    module: Module,
    source_path: str | Path,
    source_index: dict[str, tuple[dict[str, str], ...]],
) -> dict[str, str]:
    full_path = _path_text(Path(module.root) / source_path)
    sources = source_index.get(full_path)
    if sources:
        return dict(sources[0])
    source = {"path": full_path, "module_id": module.module_id, "family": module.family}
    slot = _module_source_slot(module, source_path)
    if slot:
        source["slot"] = slot
    return source


def _collection_localization_source(
    collection: Collection,
    source_path: str | Path,
    source_index: dict[str, tuple[dict[str, str], ...]],
) -> dict[str, str]:
    payload = collection.payload
    root = Path(payload.root) if isinstance(payload, CollectionSourceBundle) else Path("")
    full_path = _path_text(root / source_path)
    sources = source_index.get(full_path)
    if sources:
        return dict(sources[0])
    return {
        "path": full_path,
        "collection_id": collection.collection_id,
        "family": collection.family,
        "slot": _collection_source_slot(collection, source_path) or "loc",
    }


def _localization_owner_id(kind: str, owner: Module | Collection) -> str:
    if kind == "module" and isinstance(owner, Module):
        return owner.module_id
    if kind == "collection" and isinstance(owner, Collection):
        return f"collection:{owner.collection_id}"
    return ""


def _module_source_slot(module: Module, source_path: str | Path) -> str | None:
    normalized = _path_text(source_path)
    for slot in sorted(module.source_slots):
        for path in module.source_slots[slot]:
            if normalized == _path_text(path):
                return slot
    return None


def _collection_source_slot(collection: Collection, source_path: str | Path) -> str | None:
    payload = collection.payload
    if not isinstance(payload, CollectionSourceBundle):
        return None
    normalized = _path_text(source_path)
    for slot in sorted(payload.source_slots):
        for path in payload.source_slots[slot]:
            if normalized == _path_text(path):
                return slot
    return None


def _path_text(path: str | Path) -> str:
    return str(path).replace("\\", "/")


def _metadata_text(metadata: Mapping[str, Any], key: str) -> str | None:
    value = metadata.get(key)
    return value if isinstance(value, str) and value else None


def _metadata_int(metadata: Mapping[str, Any], key: str) -> int | None:
    value = metadata.get(key)
    if type(value) is int:
        return value
    return None
