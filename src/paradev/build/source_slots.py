"""Source-slot status inspection helpers."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path, PurePosixPath

from .._api_table import append_index_entry, append_nested_index_entry
from .manifest import manifest_rows
from .records import BuildResult, Collection
from .registry import BuildRegistry
from .slots import Slot

SOURCE_SLOTS_SCHEMA = "paradev.build.source-slots.v1"


def source_slot_status(
    result: BuildResult,
    registry: BuildRegistry,
    *,
    family: str | None = None,
    module_id: str | None = None,
    collection_id: str | None = None,
    slot: str | None = None,
    status: str | None = None,
) -> dict[str, object]:
    """Return expected source-slot contract status for a build result.

    Args:
        result: Build result with modules, collections, diagnostics, and profile.
        registry: Build registry that owns family source-slot contracts.
        family: Optional module or collection family filter.
        module_id: Optional module id filter.
        collection_id: Optional collection id filter.
        slot: Optional source slot filter.
        status: Optional slot status filter: `satisfied`, `missing`, `empty`,
            or `diagnostic`.

    Returns:
        JSON-safe source-slot status payload.
    """

    source_rows = manifest_rows(result, "sources.json")
    rows = _source_slot_rows(result, registry, source_rows)
    rows = _filter_source_slot_rows(
        rows,
        family=family,
        module_id=module_id,
        collection_id=collection_id,
        slot=slot,
        status=status,
    )
    payload: dict[str, object] = {
        "schema": SOURCE_SLOTS_SCHEMA,
        "project_id": getattr(result, "project_id", ""),
        "source_slots": rows,
        "index": _source_slot_index(rows),
    }
    profile = getattr(result, "profile", None)
    if profile:
        payload["profile"] = profile
    return payload


def _source_slot_rows(result: BuildResult, registry: BuildRegistry, source_rows: object) -> list[dict[str, object]]:
    source_lookup = _source_rows_by_owner_slot(source_rows)
    rows: list[dict[str, object]] = []
    for module in getattr(result, "modules", ()):
        module_id = getattr(module, "module_id", None)
        family = getattr(module, "family", None)
        if not isinstance(module_id, str) or not isinstance(family, str):
            continue
        for source_slots in _logical_source_slots(registry.source_slots_for(family)):
            slot_name = _logical_source_slot_name(source_slots)
            row_sources = source_lookup.get(("module", module_id, slot_name), ())
            rows.append(
                _source_slot_row(
                    owner_kind="module",
                    owner_id=module_id,
                    family=family,
                    root=getattr(module, "root", ""),
                    source_slots=source_slots,
                    source_rows=row_sources,
                    diagnostics=getattr(result, "diagnostics", ()),
                )
            )
    for collection in getattr(result, "collections", ()):
        collection_id = getattr(collection, "collection_id", None)
        family = getattr(collection, "family", None)
        if not isinstance(collection_id, str) or not isinstance(family, str):
            continue
        for source_slots in _logical_source_slots(registry.collection_source_slots_for(family)):
            slot_name = _logical_source_slot_name(source_slots)
            row_sources = source_lookup.get(("collection", collection_id, slot_name), ())
            rows.append(
                _source_slot_row(
                    owner_kind="collection",
                    owner_id=collection_id,
                    family=family,
                    root=_collection_source_root(collection),
                    source_slots=source_slots,
                    source_rows=row_sources,
                    diagnostics=getattr(result, "diagnostics", ()),
                )
            )
    return sorted(rows, key=_source_slot_row_key)


def _source_slot_row(
    *,
    owner_kind: str,
    owner_id: str,
    family: str,
    root: object,
    source_slots: tuple[Slot, ...],
    source_rows: tuple[dict[str, object], ...],
    diagnostics: object,
) -> dict[str, object]:
    source_slot = source_slots[0]
    slot_name = _logical_source_slot_name(source_slots)
    paths = _source_slot_values(source_rows, "path")
    relative_paths = _source_slot_values(source_rows, "relative_path")
    diagnostic_codes = _source_slot_diagnostic_codes(
        diagnostics,
        owner_kind=owner_kind,
        owner_id=owner_id,
        slot=slot_name,
        source_rows=source_rows,
    )
    source_statuses = _source_slot_values(source_rows, "status")
    row: dict[str, object] = {
        "owner_kind": owner_kind,
        _source_slot_owner_key(owner_kind): owner_id,
        "family": family,
        "root": str(root),
        "slot": slot_name,
        "match": getattr(source_slot, "match", ""),
        "required": any(bool(getattr(slot, "required", False)) for slot in source_slots),
        "many": any(bool(getattr(slot, "many", False)) for slot in source_slots),
        "regex": bool(getattr(source_slot, "regex", False)),
    }
    if len(source_slots) > 1:
        row["matches"] = [str(getattr(slot, "match", "")) for slot in source_slots]
    loader = _source_slot_loader(source_slots, source_rows)
    if loader:
        row["loader"] = loader
    if all(bool(getattr(slot, "shared", False)) for slot in source_slots):
        row["shared"] = True
    row.update(
        {
            "status": _source_slot_state(row["required"], source_rows, diagnostic_codes, source_statuses),
            "source_count": len(source_rows),
            "relative_paths": relative_paths,
            "paths": paths,
        }
    )
    if source_statuses:
        row["source_statuses"] = source_statuses
    suggested = _suggested_source_slot_paths(root, source_slots)
    if suggested:
        row["suggested_relative_paths"] = [relative for relative, _path in suggested]
        row["suggested_paths"] = [path for _relative, path in suggested]
    if diagnostic_codes:
        row["diagnostic_codes"] = diagnostic_codes
    return row


def _source_rows_by_owner_slot(source_rows: object) -> dict[tuple[str, str, str], tuple[dict[str, object], ...]]:
    buckets: dict[tuple[str, str, str], list[dict[str, object]]] = {}
    for row in source_rows if isinstance(source_rows, list) else ():
        if not isinstance(row, dict):
            continue
        owner_kind = row.get("owner_kind")
        slot = row.get("slot")
        if not isinstance(owner_kind, str) or not isinstance(slot, str):
            continue
        owner_id = row.get(_source_slot_owner_key(owner_kind))
        if not isinstance(owner_id, str):
            continue
        append_index_entry(buckets, (owner_kind, owner_id, slot), dict(row))
    return {key: tuple(sorted(rows, key=_source_inventory_row_key)) for key, rows in buckets.items()}


def _logical_source_slots(source_slots: tuple[Slot, ...]) -> tuple[tuple[Slot, ...], ...]:
    groups: dict[str, list[Slot]] = {}
    for source_slot in source_slots:
        append_index_entry(groups, source_slot.name, source_slot)
    return tuple(tuple(groups[name]) for name in sorted(groups))


def _logical_source_slot_name(source_slots: tuple[Slot, ...]) -> str:
    return source_slots[0].name if source_slots else ""


def _collection_source_root(collection: Collection) -> str:
    payload = collection.payload
    root = getattr(payload, "root", None)
    return str(root or "")


def _source_slot_owner_key(owner_kind: str) -> str:
    return "module_id" if owner_kind == "module" else "collection_id"


def _source_slot_loader(source_slots: tuple[Slot, ...], source_rows: tuple[dict[str, object], ...]) -> str | None:
    kinds = sorted({slot.kind for slot in source_slots if slot.kind})
    if len(kinds) == 1:
        return kinds[0]
    if len(kinds) > 1:
        return None
    loaders = _source_slot_values(source_rows, "loader")
    return loaders[0] if len(loaders) == 1 else None


def _suggested_source_slot_paths(root: object, source_slots: tuple[Slot, ...]) -> list[tuple[str, str]]:
    root_text = str(root or "")
    if not root_text:
        return []
    suggestions: dict[str, str] = {}
    for source_slot in source_slots:
        relative = _suggested_source_slot_relative_path(source_slot)
        if relative is None:
            continue
        path = Path(root_text) / Path(*PurePosixPath(relative).parts)
        suggestions[relative] = str(path)
    return [(relative, suggestions[relative]) for relative in sorted(suggestions)]


def _suggested_source_slot_relative_path(source_slot: Slot) -> str | None:
    match = getattr(source_slot, "match", "")
    if not isinstance(match, str) or not match or bool(getattr(source_slot, "regex", False)):
        return None
    if any(char in match for char in "*?[]"):
        return None
    relative = PurePosixPath(match)
    if relative.is_absolute() or any(part in {"", ".."} for part in relative.parts):
        return None
    return relative.as_posix()


def _source_slot_state(
    required: object,
    source_rows: tuple[dict[str, object], ...],
    diagnostic_codes: list[str],
    source_statuses: list[str],
) -> str:
    if not source_rows:
        return "missing" if bool(required) else "empty"
    if diagnostic_codes or "diagnostic" in source_statuses:
        return "diagnostic"
    return "satisfied"


def _source_slot_values(source_rows: tuple[dict[str, object], ...], key: str) -> list[str]:
    return sorted({value for row in source_rows if isinstance(value := row.get(key), str) and value})


def _source_slot_diagnostic_codes(
    diagnostics: object,
    *,
    owner_kind: str,
    owner_id: str,
    slot: str,
    source_rows: tuple[dict[str, object], ...],
) -> list[str]:
    codes: set[str] = set()
    for row in source_rows:
        for code in row.get("diagnostic_codes") if isinstance(row.get("diagnostic_codes"), list) else ():
            if isinstance(code, str):
                codes.add(code)
    for diagnostic in diagnostics if isinstance(diagnostics, tuple) else ():
        if not _diagnostic_matches_source_slot(diagnostic, owner_kind=owner_kind, owner_id=owner_id, slot=slot):
            continue
        code = getattr(diagnostic, "code", None)
        if isinstance(code, str):
            codes.add(code)
    return sorted(codes)


def _diagnostic_matches_source_slot(diagnostic: object, *, owner_kind: str, owner_id: str, slot: str) -> bool:
    if getattr(diagnostic, _source_slot_owner_key(owner_kind), None) != owner_id:
        return False
    diagnostic_slot = getattr(diagnostic, "slot", None)
    diagnostic_slots = getattr(diagnostic, "slots", ())
    return diagnostic_slot == slot or slot in diagnostic_slots


def _filter_source_slot_rows(
    rows: object,
    *,
    family: str | None = None,
    module_id: str | None = None,
    collection_id: str | None = None,
    slot: str | None = None,
    status: str | None = None,
) -> list[dict[str, object]]:
    filtered: list[dict[str, object]] = []
    for row in rows if isinstance(rows, list) else ():
        if not isinstance(row, dict):
            continue
        if family and row.get("family") != family:
            continue
        if module_id and row.get("module_id") != module_id:
            continue
        if collection_id and row.get("collection_id") != collection_id:
            continue
        if slot and row.get("slot") != slot:
            continue
        if status and row.get("status") != status:
            continue
        filtered.append(dict(row))
    return filtered


def _source_slot_index(rows: object) -> dict[str, object]:
    owner_index: dict[str, dict[str, list[int]]] = {}
    family_index: dict[str, list[int]] = {}
    slot_index: dict[str, list[int]] = {}
    status_index: dict[str, list[int]] = {}
    for row_index, row in enumerate(rows if isinstance(rows, list) else ()):
        if not isinstance(row, dict):
            continue
        owner_key = _source_slot_owner_index_key(row)
        slot = row.get("slot")
        if isinstance(owner_key, str) and isinstance(slot, str):
            append_nested_index_entry(owner_index, owner_key, slot, row_index)
        _append_source_slot_index(family_index, row.get("family"), row_index)
        _append_source_slot_index(slot_index, slot, row_index)
        _append_source_slot_index(status_index, row.get("status"), row_index)
    index: dict[str, object] = {}
    if owner_index:
        index["owner"] = {owner: {slot: slots[slot] for slot in sorted(slots)} for owner, slots in sorted(owner_index.items())}
    if family_index:
        index["family"] = {key: family_index[key] for key in sorted(family_index)}
    if slot_index:
        index["slot"] = {key: slot_index[key] for key in sorted(slot_index)}
    if status_index:
        index["status"] = {key: status_index[key] for key in sorted(status_index)}
    return index


def _source_slot_owner_index_key(row: Mapping[object, object]) -> str | None:
    owner_kind = row.get("owner_kind")
    if owner_kind == "module" and isinstance(row.get("module_id"), str):
        return f"module:{row['module_id']}"
    if owner_kind == "collection" and isinstance(row.get("collection_id"), str):
        return f"collection:{row['collection_id']}"
    return None


def _append_source_slot_index(bucket: dict[str, list[int]], value: object, row_index: int) -> None:
    if isinstance(value, str) and value:
        append_index_entry(bucket, value, row_index)


def _source_slot_row_key(row: Mapping[str, object]) -> tuple[str, str, str]:
    owner_kind = str(row.get("owner_kind") or "")
    owner_id = row.get(_source_slot_owner_key(owner_kind))
    return (owner_kind, owner_id if isinstance(owner_id, str) else "", str(row.get("slot") or ""))


def _source_inventory_row_key(row: Mapping[str, object]) -> tuple[str, str, str, str]:
    owner_kind = str(row.get("owner_kind") or "")
    owner_id = row.get(_source_slot_owner_key(owner_kind))
    return (
        owner_kind,
        owner_id if isinstance(owner_id, str) else "",
        str(row.get("slot") or ""),
        str(row.get("relative_path") or ""),
    )
