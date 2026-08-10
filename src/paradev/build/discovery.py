"""Source-root module discovery for project builds."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Mapping, Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, replace
from pathlib import Path
from typing import TypeVar, cast

from .loaders import load_collection_sources, load_module_sources
from .records import Collection, Diagnostic, Module
from .slots import Slot, match_slots

DEFAULT_MODULE_SLOTS = (
    Slot("def", "def.txt", kind="pdx"),
    Slot("loc", "**/*.loc", many=True, kind="loc"),
    Slot("icon", r"^(icon|goal|portrait|picture)\.(png|dds|tga)$", regex=True, kind="copy"),
    Slot("copy", "copy/*", many=True, kind="copy"),
    Slot("assets", "assets/*", many=True, kind="copy"),
)
DEFAULT_COLLECTION_SLOTS = (
    Slot("def", "def.txt", kind="pdx"),
    Slot("loc", "**/*.loc", many=True, kind="loc"),
)

_ResultT = TypeVar("_ResultT")
_MAX_DISCOVERY_WORKERS = 4


@dataclass(frozen=True, slots=True)
class ModuleDiscoveryResult:
    """Discovered source modules and diagnostics."""

    modules: tuple[Module, ...]
    diagnostics: tuple[Diagnostic, ...] = ()
    cache_hits: int = 0
    cache_misses: int = 0
    cache_refreshes: int = 0
    cached_records: int = 0
    cache_signature: str | None = None


@dataclass(frozen=True, slots=True)
class CollectionDiscoveryResult:
    """Discovered collection descriptors and diagnostics."""

    collections: tuple[Collection, ...]
    diagnostics: tuple[Diagnostic, ...] = ()
    cache_hits: int = 0
    cache_misses: int = 0
    cache_refreshes: int = 0
    cached_records: int = 0
    cache_signature: str | None = None


def discover_modules(
    source_roots: Sequence[str | Path],
    slots: Sequence[Slot] = DEFAULT_MODULE_SLOTS,
    slots_by_family: Mapping[str, Sequence[Slot]] | None = None,
    metadata_keys_by_family: Mapping[str, Sequence[str]] | None = None,
    strict_metadata: bool = False,
    family: str | None = None,
    module_id: str | None = None,
    collection_id: str | None = None,
    _cache_root: str | Path | None = None,
    _cache_read: bool = True,
    _cache_write: bool = True,
    _parallelism: int = 1,
) -> ModuleDiscoveryResult:
    """Discover source modules under project source roots.

    Args:
        source_roots: Project source roots.
        slots: Default slot declarations to match inside each module root.
        slots_by_family: Optional family-specific slot declarations.
        metadata_keys_by_family: Optional family-specific metadata keys.
        strict_metadata: Whether unknown module metadata keys should be
            blocking errors instead of loose-mode warnings.
        family: Optional exact family folder to inspect.
        module_id: Optional exact `family/object_id` module to inspect.
        collection_id: Optional exact collection id membership to include.

    Returns:
        Discovered modules and diagnostics.
    """

    modules: list[Module] = []
    diagnostics: list[Diagnostic] = []
    cache_hits = 0
    cache_misses = 0
    cache_refreshes = 0
    cached_records = 0
    cache_signature_rows: list[dict[str, object]] = []
    cache_signature_complete = True
    default_slots = tuple(slots)
    family_slots = {family: tuple(items) for family, items in (slots_by_family or {}).items()}
    family_metadata_keys = {family: tuple(items) for family, items in (metadata_keys_by_family or {}).items()}
    module_family, module_object_id = _module_id_filter(module_id)
    family_filter = module_family or family
    if family is not None and module_family is not None and family != module_family:
        return ModuleDiscoveryResult(modules=(), diagnostics=())
    for source_root in sorted(Path(path) for path in source_roots):
        modules_root = source_root / "modules"
        if not modules_root.is_dir():
            continue

        def discover_family(
            family_root: Path,
        ) -> tuple[str, ModuleDiscoveryResult, str | None, int, str | None]:
            family_id = family_root.name
            slots_for_family = family_slots.get(family_id, default_slots)
            metadata_keys = family_metadata_keys.get(family_id, ())

            def load_family() -> ModuleDiscoveryResult:
                return _discover_module_family(
                    family_root,
                    slots=slots_for_family,
                    metadata_keys=metadata_keys,
                    strict_metadata=strict_metadata,
                )

            if _cache_root is not None:
                from .source_cache import cached_module_family

                cached = cached_module_family(
                    Path(_cache_root),
                    source_root=source_root,
                    family_root=family_root,
                    slots=slots_for_family,
                    metadata_keys=metadata_keys,
                    strict_metadata=strict_metadata,
                    read=_cache_read,
                    write=_cache_write,
                    loader=load_family,
                )
                family_result = cast(ModuleDiscoveryResult, cached.result)
                cache_status: str | None = cached.status
                record_count = cached.record_count
                cache_signature = cached.signature
            else:
                family_result = load_family()
                cache_status = None
                record_count = 0
                cache_signature = None
            return (
                family_id,
                family_result,
                cache_status,
                record_count,
                cache_signature,
            )

        family_roots = tuple(_matching_family_dirs(modules_root, family_filter))
        family_signatures: list[tuple[str, str]] = []
        for (
            family_id,
            family_result,
            cache_status,
            record_count,
            cache_signature,
        ) in _run_discovery_jobs(
            family_roots,
            discover_family,
            parallelism=_parallelism,
        ):
            if cache_signature is not None:
                family_signatures.append((family_id, cache_signature))
            else:
                cache_signature_complete = False
            if cache_status == "hit":
                cache_hits += 1
                cached_records += record_count
            elif cache_status == "miss":
                cache_misses += 1
            elif cache_status == "refresh":
                cache_refreshes += 1
            family_result = _filter_module_family_result(
                family_result,
                family_id=family_id,
                module_object_id=module_object_id,
                collection_id=collection_id,
            )
            modules.extend(family_result.modules)
            diagnostics.extend(family_result.diagnostics)
        if _cache_root is not None:
            cache_signature_rows.append(
                {
                    "source_root": str(source_root.resolve()),
                    "families": family_signatures,
                }
            )
    return ModuleDiscoveryResult(
        modules=tuple(sorted(modules, key=lambda item: item.module_id)),
        diagnostics=tuple(diagnostics),
        cache_hits=cache_hits,
        cache_misses=cache_misses,
        cache_refreshes=cache_refreshes,
        cached_records=cached_records,
        cache_signature=(_discovery_cache_signature("modules", cache_signature_rows) if _cache_root is not None and cache_signature_complete else None),
    )


def discover_collections(
    source_roots: Sequence[str | Path],
    slots: Sequence[Slot] = DEFAULT_COLLECTION_SLOTS,
    slots_by_family: Mapping[str, Sequence[Slot]] | None = None,
    metadata_keys_by_family: Mapping[str, Sequence[str]] | None = None,
    strict_metadata: bool = False,
    family: str | None = None,
    collection_id: str | None = None,
    module_id: str | None = None,
    _cache_root: str | Path | None = None,
    _cache_read: bool = True,
    _cache_write: bool = True,
    _parallelism: int = 1,
) -> CollectionDiscoveryResult:
    """Discover collection descriptors under project source roots.

    Args:
        source_roots: Project source roots.
        slots: Default collection descriptor slot declarations.
        slots_by_family: Optional family-specific descriptor slot declarations.
        metadata_keys_by_family: Optional family-specific metadata keys.
        strict_metadata: Whether unknown descriptor metadata keys should be
            blocking errors instead of loose-mode warnings.
        family: Optional exact collection family folder to inspect.
        collection_id: Optional exact collection descriptor id to inspect.
        module_id: Optional exact member module id to include.

    Returns:
        Discovered collection descriptors and diagnostics.
    """

    collections: list[Collection] = []
    diagnostics: list[Diagnostic] = []
    cache_hits = 0
    cache_misses = 0
    cache_refreshes = 0
    cached_records = 0
    cache_signature_rows: list[dict[str, object]] = []
    cache_signature_complete = True
    default_slots = tuple(slots)
    family_slots = {family: tuple(items) for family, items in (slots_by_family or {}).items()}
    family_metadata_keys = {family: tuple(items) for family, items in (metadata_keys_by_family or {}).items()}
    module_family, _module_object_id = _module_id_filter(module_id)
    family_filter = family or module_family
    for source_root in sorted(Path(path) for path in source_roots):
        collections_root = source_root / "collections"
        if not collections_root.is_dir():
            continue

        def discover_family(
            family_root: Path,
        ) -> tuple[
            str,
            CollectionDiscoveryResult,
            str | None,
            int,
            str | None,
        ]:
            family_id = family_root.name
            slots_for_family = family_slots.get(family_id, default_slots)
            metadata_keys = family_metadata_keys.get(family_id, ())

            def load_family() -> CollectionDiscoveryResult:
                return _discover_collection_family(
                    family_root,
                    slots=slots_for_family,
                    metadata_keys=metadata_keys,
                    strict_metadata=strict_metadata,
                )

            if _cache_root is not None:
                from .source_cache import cached_collection_family

                cached = cached_collection_family(
                    Path(_cache_root),
                    source_root=source_root,
                    family_root=family_root,
                    slots=slots_for_family,
                    metadata_keys=metadata_keys,
                    strict_metadata=strict_metadata,
                    read=_cache_read,
                    write=_cache_write,
                    loader=load_family,
                )
                family_result = cast(CollectionDiscoveryResult, cached.result)
                cache_status: str | None = cached.status
                record_count = cached.record_count
                cache_signature = cached.signature
            else:
                family_result = load_family()
                cache_status = None
                record_count = 0
                cache_signature = None
            return (
                family_id,
                family_result,
                cache_status,
                record_count,
                cache_signature,
            )

        family_roots = tuple(_matching_family_dirs(collections_root, family_filter))
        family_signatures: list[tuple[str, str]] = []
        for (
            family_id,
            family_result,
            cache_status,
            record_count,
            cache_signature,
        ) in _run_discovery_jobs(
            family_roots,
            discover_family,
            parallelism=_parallelism,
        ):
            if cache_signature is not None:
                family_signatures.append((family_id, cache_signature))
            else:
                cache_signature_complete = False
            if cache_status == "hit":
                cache_hits += 1
                cached_records += record_count
            elif cache_status == "miss":
                cache_misses += 1
            elif cache_status == "refresh":
                cache_refreshes += 1
            family_result = _filter_collection_family_result(
                family_result,
                collection_id=collection_id,
                module_id=module_id,
            )
            collections.extend(family_result.collections)
            diagnostics.extend(family_result.diagnostics)
        if _cache_root is not None:
            cache_signature_rows.append(
                {
                    "source_root": str(source_root.resolve()),
                    "families": family_signatures,
                }
            )
    return CollectionDiscoveryResult(
        collections=tuple(sorted(collections, key=lambda item: (item.family, item.collection_id))),
        diagnostics=tuple(diagnostics),
        cache_hits=cache_hits,
        cache_misses=cache_misses,
        cache_refreshes=cache_refreshes,
        cached_records=cached_records,
        cache_signature=(_discovery_cache_signature("collections", cache_signature_rows) if _cache_root is not None and cache_signature_complete else None),
    )


def _run_discovery_jobs(
    family_roots: Sequence[Path],
    discover: Callable[[Path], _ResultT],
    *,
    parallelism: int,
) -> tuple[_ResultT, ...]:
    """Run independent family discovery in deterministic source order."""

    workers = min(_MAX_DISCOVERY_WORKERS, max(1, int(parallelism)))
    if workers == 1 or len(family_roots) <= 1:
        return tuple(discover(root) for root in family_roots)
    with ThreadPoolExecutor(max_workers=min(workers, len(family_roots))) as executor:
        futures = tuple(executor.submit(discover, root) for root in family_roots)
        return tuple(future.result() for future in futures)


def _discovery_cache_signature(
    kind: str,
    rows: Sequence[Mapping[str, object]],
) -> str:
    """Return a deterministic aggregate of the active family signatures."""

    payload = json.dumps(
        {"kind": kind, "source_roots": list(rows)},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _discover_module_family(
    family_root: Path,
    *,
    slots: tuple[Slot, ...],
    metadata_keys: Sequence[str],
    strict_metadata: bool,
) -> ModuleDiscoveryResult:
    family_id = family_root.name
    modules: list[Module] = []
    diagnostics: list[Diagnostic] = []
    for module_root in _matching_object_dirs(family_root, None):
        module_id = f"{family_id}/{_object_id(module_root.name)}"
        matched = match_slots(module_root, slots, module_id=module_id)
        if not _module_candidate(module_root, matched.source_slots):
            continue
        bundle = load_module_sources(
            module_root,
            matched.source_slots,
            module_id=module_id,
            inferred_type=family_id,
            slots=slots,
            metadata_keys=metadata_keys,
            strict_metadata=strict_metadata,
        )
        modules.append(bundle.to_module(family=family_id))
        diagnostics.extend(_diagnostic_family(diagnostic, family_id) for diagnostic in (*matched.diagnostics, *bundle.diagnostics))
    return ModuleDiscoveryResult(
        modules=tuple(sorted(modules, key=lambda item: item.module_id)),
        diagnostics=tuple(diagnostics),
    )


def _discover_collection_family(
    family_root: Path,
    *,
    slots: tuple[Slot, ...],
    metadata_keys: Sequence[str],
    strict_metadata: bool,
) -> CollectionDiscoveryResult:
    family_id = family_root.name
    collections: list[Collection] = []
    diagnostics: list[Diagnostic] = []
    for collection_root in _matching_object_dirs(family_root, None):
        matched = match_slots(collection_root, slots)
        if not _collection_candidate(collection_root, matched.source_slots):
            continue
        result = load_collection_sources(
            collection_root,
            family=family_id,
            collection_id=_object_id(collection_root.name),
            source_slots=matched.source_slots,
            slots=slots,
            metadata_keys=metadata_keys,
            strict_metadata=strict_metadata,
        )
        collections.append(result.collection)
        diagnostics.extend(_diagnostic_family(diagnostic, family_id) for diagnostic in (*matched.diagnostics, *result.diagnostics))
    return CollectionDiscoveryResult(
        collections=tuple(
            sorted(
                collections,
                key=lambda item: (item.family, item.collection_id),
            )
        ),
        diagnostics=tuple(diagnostics),
    )


def _filter_module_family_result(
    result: ModuleDiscoveryResult,
    *,
    family_id: str,
    module_object_id: str | None,
    collection_id: str | None,
) -> ModuleDiscoveryResult:
    modules = tuple(
        module
        for module in result.modules
        if (module_object_id is None or module.module_id == f"{family_id}/{module_object_id}")
        and (collection_id is None or module.collection_id == collection_id)
    )
    if module_object_id is None and collection_id is None:
        return result
    module_ids = {module.module_id for module in modules}
    diagnostics = tuple(diagnostic for diagnostic in result.diagnostics if diagnostic.module_id is None or diagnostic.module_id in module_ids)
    return ModuleDiscoveryResult(
        modules=modules,
        diagnostics=diagnostics,
        cache_hits=result.cache_hits,
        cache_misses=result.cache_misses,
        cache_refreshes=result.cache_refreshes,
        cached_records=result.cached_records,
    )


def _filter_collection_family_result(
    result: CollectionDiscoveryResult,
    *,
    collection_id: str | None,
    module_id: str | None,
) -> CollectionDiscoveryResult:
    collections = tuple(
        collection
        for collection in result.collections
        if (collection_id is None or collection.collection_id == collection_id) and (module_id is None or module_id in collection.module_ids)
    )
    if collection_id is None and module_id is None:
        return result
    collection_ids = {collection.collection_id for collection in collections}
    diagnostics = tuple(diagnostic for diagnostic in result.diagnostics if diagnostic.collection_id is None or diagnostic.collection_id in collection_ids)
    return CollectionDiscoveryResult(
        collections=collections,
        diagnostics=diagnostics,
        cache_hits=result.cache_hits,
        cache_misses=result.cache_misses,
        cache_refreshes=result.cache_refreshes,
        cached_records=result.cached_records,
    )


def _child_dirs(root: Path) -> tuple[Path, ...]:
    return tuple(sorted((path for path in root.iterdir() if path.is_dir()), key=lambda path: path.name))


def _diagnostic_family(diagnostic: Diagnostic, family: str) -> Diagnostic:
    """Attach the discovery family needed to disambiguate repeated ids."""

    if diagnostic.family is not None:
        return diagnostic
    return replace(diagnostic, family=family)


def _matching_family_dirs(root: Path, family: str | None) -> tuple[Path, ...]:
    if family is None:
        return _child_dirs(root)
    family_root = root / family
    return (family_root,) if family_root.is_dir() else ()


def _matching_object_dirs(root: Path, object_id: str | None) -> tuple[Path, ...]:
    if object_id is None:
        return _child_dirs(root)
    direct = root / object_id
    matches = {direct} if direct.is_dir() else set()
    matches.update(path for path in _child_dirs(root) if _object_id(path.name) == object_id)
    return tuple(sorted(matches, key=lambda path: path.name))


def _module_id_filter(module_id: str | None) -> tuple[str | None, str | None]:
    if module_id is None:
        return None, None
    parts = module_id.split("/", 1)
    if len(parts) != 2:
        return None, None
    family, object_id = (part.strip() for part in parts)
    if not family or not object_id:
        return None, None
    return family, object_id


def _module_candidate(root: Path, source_slots: Mapping[str, Sequence[str]]) -> bool:
    return (root / "meta.yaml").is_file() or any(source_slots.values())


def _collection_candidate(root: Path, source_slots: Mapping[str, Sequence[str]]) -> bool:
    return (root / "meta.yaml").is_file() or (root / "collection.yaml").is_file() or any(source_slots.values())


def _object_id(name: str) -> str:
    return name.split(" - ", 1)[0].strip()
