"""Filtered build manifest views for SDK and surface adapters."""

from __future__ import annotations

import unicodedata
from collections.abc import Mapping, Sequence
from os import PathLike, fsencode, scandir
from pathlib import Path, PurePosixPath

from paradev._api_table import append_index_entry
from paradev.localization import canonical_language

from .manifest import (
    _summary_payload,
    artifact_collection_ids,
    artifact_index,
    artifact_module_ids,
    asset_index,
    collection_index,
    dependency_index,
    diagnostic_family_index,
    diagnostic_index,
    localization_index,
    manifest_payloads,
    module_index,
    source_inventory_index,
    source_map_index,
    sprite_index,
)
from .records import BuildResult
from .registry import BuildRegistry
from .slots import match_slots

FAMILIES_SCHEMA = "paradev.build.families.v1"
MANIFESTS_SCHEMA = "paradev.build.manifests.v1"
AUTHORING_PATH_SCHEMA = "paradev.sdk.authoring_path.v1"
AUTHORING_PLAN_SCHEMA = "paradev.sdk.authoring_plan.v1"
MODULE_PATH_TEMPLATE = "modules/{family}/{object_id}"
COLLECTION_PATH_TEMPLATE = "collections/{family}/{collection_id}"


def families_view(
    registry: BuildRegistry,
    *,
    project_id: str,
    profile: str,
    project_root: str | Path,
    source_roots: Sequence[str | Path],
    family: str | None = None,
    kind: str | None = None,
    source_slot: str | None = None,
    collection_source_slot: str | None = None,
    sprite_slot: str | None = None,
    route: str | None = None,
    artifact_type: str | None = None,
) -> dict[str, object]:
    """Return build-family contracts with project authoring context.

    Args:
        registry: Build registry to inspect.
        project_id: Stable project identifier.
        profile: Build profile identifier.
        project_root: Project root used for relative source-root display.
        source_roots: Project source roots in authoring priority order.
        family: Optional exact family id filter.
        kind: Optional exact compiler kind filter.
        source_slot: Optional module source-slot filter.
        collection_source_slot: Optional collection descriptor source-slot filter.
        sprite_slot: Optional sprite source-slot filter.
        route: Optional routed-source route id filter.
        artifact_type: Optional output and writer artifact type filter.

    Returns:
        JSON-safe authoring, family, and artifact-writer capability payload.
    """

    return {
        "schema": FAMILIES_SCHEMA,
        "project_id": project_id,
        "profile": profile,
        "authoring": authoring_view(Path(project_root), tuple(Path(source_root) for source_root in source_roots)),
        **registry.to_view(
            family=family,
            kind=kind,
            source_slot=source_slot,
            collection_source_slot=collection_source_slot,
            sprite_slot=sprite_slot,
            route=route,
            artifact_type=artifact_type,
        ),
    }


def authoring_view(project_root: str | PathLike[str], source_roots: Sequence[str | PathLike[str]]) -> dict[str, object]:
    """Return source-root and folder-template authoring context.

    Args:
        project_root: Project root used for relative source-root display.
        source_roots: Project source roots in authoring priority order.

    Returns:
        JSON-safe source-root and folder-template payload.
    """

    root = _project_root(project_root)
    roots = _project_source_roots(root, source_roots)
    return {
        "source_roots": _source_root_views(root, roots),
        "module_path_template": MODULE_PATH_TEMPLATE,
        "collection_path_template": COLLECTION_PATH_TEMPLATE,
    }


def authoring_path_view(
    *,
    project_id: str,
    project_root: str | PathLike[str],
    source_roots: Sequence[str | PathLike[str]],
    kind: str,
    family: str,
    target_id: str,
    source_root: str | PathLike[str] | None = None,
    folder_name: str | None = None,
) -> dict[str, object]:
    """Return the canonical source folder for a module or collection.

    Args:
        project_id: Stable project identifier.
        project_root: Project root used to resolve relative source roots.
        source_roots: Configured project source roots in authoring priority order.
        kind: Authoring target kind, either `module` or `collection`.
        family: Registered or project-local family path segment.
        target_id: Module object id or collection id path segment.
        source_root: Optional configured source root path. Relative values
            resolve from the project root. Defaults to the first source root.
        folder_name: Internal physical resource-folder override for scaffold
            planning. The logical id remains `target_id`.

    Returns:
        JSON-safe authoring path payload. This helper never writes files.

    Raises:
        ValueError: If the kind, family, target id, or source root is invalid.
    """

    root = _project_root(project_root)
    roots = _project_source_roots(root, source_roots)
    target_kind = _authoring_kind(kind)
    clean_family = _authoring_path_token(family, "family")
    selected_source_root = _select_source_root(root, roots, source_root)
    if target_kind == "module":
        clean_id = _authoring_module_object_id_token(target_id)
        physical_folder_name = (
            _authoring_module_folder_name(folder_name, object_id=clean_id)
            if folder_name is not None
            else _existing_authoring_module_folder_name(
                selected_source_root / "modules" / clean_family,
                object_id=clean_id,
            )
        )
        relative_root = MODULE_PATH_TEMPLATE.format(
            family=clean_family,
            object_id=physical_folder_name,
        )
        target_root = selected_source_root / relative_root
        return {
            "schema": AUTHORING_PATH_SCHEMA,
            "project_id": project_id,
            "kind": target_kind,
            "family": clean_family,
            "object_id": clean_id,
            "module_id": f"{clean_family}/{clean_id}",
            "source_root": str(selected_source_root),
            "source_root_relative_path": _project_relative_path(root, selected_source_root),
            "root": str(target_root),
            "relative_path": _project_relative_path(root, target_root),
            "template": MODULE_PATH_TEMPLATE,
            "exists": target_root.exists(),
        }

    clean_id = _authoring_path_token(target_id, "collection_id")
    physical_folder_name = (
        _authoring_module_folder_name(folder_name, object_id=clean_id)
        if folder_name is not None
        else _existing_authoring_module_folder_name(
            selected_source_root / "collections" / clean_family,
            object_id=clean_id,
        )
    )
    relative_root = COLLECTION_PATH_TEMPLATE.format(
        family=clean_family,
        collection_id=physical_folder_name,
    )
    target_root = selected_source_root / relative_root
    return {
        "schema": AUTHORING_PATH_SCHEMA,
        "project_id": project_id,
        "kind": target_kind,
        "family": clean_family,
        "collection_id": clean_id,
        "source_root": str(selected_source_root),
        "source_root_relative_path": _project_relative_path(root, selected_source_root),
        "root": str(target_root),
        "relative_path": _project_relative_path(root, target_root),
        "template": COLLECTION_PATH_TEMPLATE,
        "exists": target_root.exists(),
    }


def authoring_plan_view(
    registry: BuildRegistry,
    *,
    project_id: str,
    profile: str,
    project_root: str | PathLike[str],
    source_roots: Sequence[str | PathLike[str]],
    kind: str,
    family: str,
    target_id: str,
    source_root: str | PathLike[str] | None = None,
    folder_name: str | None = None,
) -> dict[str, object]:
    """Return a read-only authoring destination plus expected source slots.

    Args:
        registry: Build registry that owns the selected family contract.
        project_id: Stable project identifier.
        profile: Build profile identifier.
        project_root: Project root used to resolve relative source roots.
        source_roots: Configured project source roots in authoring priority order.
        kind: Authoring target kind, either `module` or `collection`.
        family: Registered or project-local family path segment.
        target_id: Module object id or collection id path segment.
        source_root: Optional configured source root path.
        folder_name: Internal physical resource-folder override for scaffold
            planning. The logical id remains `target_id`.

    Returns:
        JSON-safe payload for GUI, CLI, MCP, REST, and importer preflight flows.

    Raises:
        ValueError: If the requested authoring path or family is invalid.
    """

    path_payload = authoring_path_view(
        project_id=project_id,
        project_root=project_root,
        source_roots=source_roots,
        kind=kind,
        family=family,
        target_id=target_id,
        source_root=source_root,
        folder_name=folder_name,
    )
    family_row = _authoring_family_row(registry, str(path_payload["family"]))
    slot_key = "source_slots" if path_payload["kind"] == "module" else "collection_source_slots"
    source_slot_contracts = (
        registry.source_slots_for(str(path_payload["family"]))
        if path_payload["kind"] == "module"
        else registry.collection_source_slots_for(str(path_payload["family"]))
    )
    match_result = match_slots(
        str(path_payload["root"]),
        source_slot_contracts,
        module_id=str(path_payload["module_id"]) if path_payload["kind"] == "module" else None,
    )
    rows = _authoring_slot_rows(
        path_payload,
        family_row.get(slot_key),
        owner_kind=str(path_payload["kind"]),
        matched_slots=match_result.source_slots,
        diagnostics=match_result.diagnostics,
        default_assets=_family_default_assets(family_row),
    )
    return {
        "schema": AUTHORING_PLAN_SCHEMA,
        "project_id": project_id,
        "profile": profile,
        "authoring_path": path_payload,
        "source_slots": rows,
        "index": _authoring_slot_index(rows),
    }


def _source_root_views(project_root: Path, source_roots: tuple[Path, ...]) -> list[dict[str, object]]:
    return [
        {
            "path": str(source_root),
            "relative_path": _project_relative_path(project_root, source_root),
            "default": index == 0,
        }
        for index, source_root in enumerate(source_roots)
    ]


def _project_root(value: str | PathLike[str]) -> Path:
    return Path(value).expanduser().resolve()


def _project_source_roots(project_root: Path, source_roots: Sequence[str | PathLike[str]]) -> tuple[Path, ...]:
    roots: list[Path] = []
    for source_root in source_roots:
        candidate = Path(source_root).expanduser()
        if not candidate.is_absolute():
            candidate = project_root / candidate
        roots.append(candidate.resolve())
    return tuple(roots)


def _select_source_root(
    project_root: Path,
    source_roots: tuple[Path, ...],
    source_root: str | PathLike[str] | None,
) -> Path:
    if not source_roots:
        raise ValueError("Project has no configured source roots.")
    if source_root is None:
        return source_roots[0]
    candidate = Path(source_root).expanduser()
    if not candidate.is_absolute():
        candidate = project_root / candidate
    resolved = candidate.resolve()
    for configured in source_roots:
        if configured == resolved:
            return configured
    available = ", ".join(_project_relative_path(project_root, configured) for configured in source_roots)
    raise ValueError(f"Unknown source root {source_root!s}. Available source roots: {available}.")


def _authoring_kind(value: str) -> str:
    text = value.strip() if isinstance(value, str) else ""
    if text not in {"module", "collection"}:
        raise ValueError("Authoring kind must be 'module' or 'collection'.")
    return text


def _authoring_path_token(value: object, key: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Authoring {key} must be a non-empty path segment.")
    text = value.strip()
    if text in {".", ".."} or "/" in text or "\\" in text or any(char.isspace() for char in text):
        raise ValueError(f"Authoring {key} must be one path segment.")
    return text


def _authoring_module_object_id_token(value: object) -> str:
    """Validate a logical module id, including existing ids with spaces."""

    if not isinstance(value, str) or not value.strip():
        raise ValueError("Authoring object_id must be a non-empty path segment.")
    text = value.strip()
    if text in {".", ".."} or "/" in text or "\\" in text or any(ord(character) < 32 or ord(character) == 127 for character in text):
        raise ValueError("Authoring object_id must be one path segment.")
    return text


def _existing_authoring_module_folder_name(
    family_root: Path,
    *,
    object_id: str,
) -> str:
    """Return the unique physical folder for one logical module id."""

    logical_key = _portable_authoring_name_key(object_id)
    try:
        with scandir(family_root) as entries:
            matches = sorted(
                (
                    (entry.name, entry.is_dir(follow_symlinks=False))
                    for entry in entries
                    if _portable_authoring_name_key(_authoring_module_object_id(entry.name)) == logical_key
                ),
                key=lambda item: (
                    _portable_authoring_name_key(item[0]),
                    item[0],
                ),
            )
    except FileNotFoundError:
        return object_id
    except NotADirectoryError as error:
        raise ValueError(f"Module family source path is not a directory: {family_root}.") from error
    except OSError as error:
        raise ValueError(f"Module family source path could not be inspected: {family_root}: {error}.") from error
    if not matches:
        return object_id
    if len(matches) > 1:
        names = ", ".join(name for name, _is_directory in matches)
        raise ValueError(f"Module {object_id!r} has multiple physical folders under " f"{family_root}: {names}.")

    folder_name, is_directory = matches[0]
    if not is_directory:
        raise ValueError(f"Module source path is not a directory: {family_root / folder_name}.")
    existing_object_id = _authoring_module_object_id(folder_name)
    if existing_object_id != object_id:
        raise ValueError(f"Module folder {folder_name!r} collides with logical object id " f"{object_id!r} by case or Unicode normalization.")
    if folder_name != object_id:
        prefix = f"{object_id} - "
        title = folder_name[len(prefix) :] if folder_name.startswith(prefix) else ""
        if not title:
            raise ValueError(f"Module folder {folder_name!r} does not have a valid human-readable suffix.")
    # Existing real directories remain addressable even when a legacy display
    # suffix contains characters that new scaffold targets reject. Logical-id
    # alias checks above still fail closed, while users can rename/migrate the
    # physical folder without losing GUI access first.
    return folder_name


def _authoring_module_folder_name(value: object, *, object_id: str) -> str:
    """Validate one physical module-folder override."""

    if not isinstance(value, str) or not value:
        raise ValueError("Authoring folder_name must be a non-empty path segment.")
    if value != value.strip() or (value != object_id and unicodedata.normalize("NFC", value) != value):
        raise ValueError("Authoring folder_name must use normalized text without surrounding whitespace.")
    if value in {".", ".."} or "/" in value or "\\" in value:
        raise ValueError("Authoring folder_name must be exactly one path segment.")
    invalid_character = next(
        (character for character in value if ord(character) < 32 or ord(character) == 127 or character in '<>:"|?*'),
        None,
    )
    if invalid_character is not None:
        raise ValueError(f"Authoring folder_name contains non-portable character " f"{invalid_character!r}.")
    if value.endswith((".", " ")):
        raise ValueError("Authoring folder_name cannot end with a dot or space.")
    if len(fsencode(value)) > 255:
        raise ValueError("Authoring folder_name exceeds the portable 255-byte filename limit.")
    if _authoring_module_object_id(value) != object_id:
        raise ValueError(f"Authoring folder_name must begin with the exact logical object id " f"{object_id!r}, optionally followed by ' - title'.")
    if value != object_id:
        prefix = f"{object_id} - "
        title = value[len(prefix) :] if value.startswith(prefix) else ""
        if not title or title != title.strip():
            raise ValueError(f"Authoring folder_name must be {object_id!r} or begin with " f"{prefix!r} followed by a title.")
    return value


def _authoring_module_object_id(folder_name: str) -> str:
    """Return the logical module id prefix from one physical folder name."""

    return folder_name.split(" - ", 1)[0].strip()


def _portable_authoring_name_key(value: str) -> str:
    """Return a portable case- and Unicode-insensitive name key."""

    return unicodedata.normalize("NFC", value).casefold()


def _project_relative_path(root: Path, target: Path) -> str:
    try:
        return target.relative_to(root).as_posix()
    except ValueError:
        return str(target)


def _authoring_family_row(registry: BuildRegistry, family: str) -> dict[str, object]:
    rows = registry.to_view(family=family).get("families")
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"Unknown build family {family!r}.")
    row = rows[0]
    return dict(row) if isinstance(row, Mapping) else {}


def _authoring_slot_rows(
    authoring_path: Mapping[str, object],
    slots: object,
    *,
    owner_kind: str,
    matched_slots: Mapping[str, Sequence[str]],
    diagnostics: object,
    default_assets: Mapping[str, Mapping[str, object]] | None = None,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    root = Path(str(authoring_path["root"]))
    relative_root = str(authoring_path["relative_path"])
    family = str(authoring_path["family"])
    owner_key = _authoring_owner_key(owner_kind)
    owner_id = str(authoring_path[owner_key])
    for source_slots in _logical_authoring_slots(slots):
        row = _authoring_slot_row(
            source_slots,
            owner_kind=owner_kind,
            owner_key=owner_key,
            owner_id=owner_id,
            family=family,
            root=root,
            relative_root=relative_root,
            matched_slots=matched_slots,
            diagnostics=diagnostics,
            default_assets=default_assets or {},
        )
        rows.append(row)
    return rows


def _authoring_slot_row(
    source_slots: tuple[dict[str, object], ...],
    *,
    owner_kind: str,
    owner_key: str,
    owner_id: str,
    family: str,
    root: Path,
    relative_root: str,
    matched_slots: Mapping[str, Sequence[str]],
    diagnostics: object,
    default_assets: Mapping[str, Mapping[str, object]],
) -> dict[str, object]:
    source_slot = source_slots[0]
    slot_name = str(source_slot.get("name"))
    relative_paths = _matched_authoring_slot_paths(matched_slots.get(slot_name, ()))
    diagnostic_codes = _authoring_slot_diagnostic_codes(diagnostics, slot_name)
    row: dict[str, object] = {
        "owner_kind": owner_kind,
        owner_key: owner_id,
        "family": family,
        "root": str(root),
        "slot": slot_name,
        "match": str(source_slot.get("match")),
        "required": any(bool(slot.get("required")) for slot in source_slots),
        "many": any(bool(slot.get("many")) for slot in source_slots),
        "regex": bool(source_slot.get("regex")),
    }
    if len(source_slots) > 1:
        row["matches"] = [str(slot.get("match")) for slot in source_slots]
    loader = _authoring_slot_loader(source_slots)
    if loader:
        row["loader"] = loader
    if all(bool(slot.get("shared")) for slot in source_slots):
        row["shared"] = True
    default_asset = _slot_default_asset(default_assets, slot_name)
    if default_asset:
        row["default_asset"] = default_asset
    row.update(
        {
            "status": _authoring_slot_state(row["required"], relative_paths, diagnostic_codes),
            "source_count": len(relative_paths),
            "relative_paths": relative_paths,
            "paths": [str(root / Path(*PurePosixPath(relative_path).parts)) for relative_path in relative_paths],
        }
    )
    if diagnostic_codes:
        row["diagnostic_codes"] = diagnostic_codes
    suggested = _suggested_authoring_paths(root, relative_root, source_slots)
    if suggested:
        row["suggested_relative_paths"] = [relative for relative, _path in suggested]
        row["suggested_paths"] = [str(path) for _relative, path in suggested]
    return row


def _family_default_assets(row: Mapping[str, object]) -> dict[str, dict[str, object]]:
    assets = row.get("assets")
    if not isinstance(assets, Mapping):
        return {}
    defaults = assets.get("defaults")
    if not isinstance(defaults, Mapping):
        return {}
    return {str(slot): dict(asset) for slot, asset in defaults.items() if isinstance(slot, str) and slot and isinstance(asset, Mapping)}


def _slot_default_asset(default_assets: Mapping[str, Mapping[str, object]], slot: str) -> dict[str, object]:
    asset = default_assets.get(slot)
    return dict(asset) if isinstance(asset, Mapping) else {}


def _matched_authoring_slot_paths(paths: Sequence[str]) -> list[str]:
    return sorted({str(path).replace("\\", "/") for path in paths if str(path)})


def _authoring_slot_diagnostic_codes(diagnostics: object, slot: str) -> list[str]:
    codes: set[str] = set()
    for diagnostic in diagnostics if isinstance(diagnostics, tuple) else ():
        diagnostic_slot = getattr(diagnostic, "slot", None)
        diagnostic_slots = tuple(str(value) for value in getattr(diagnostic, "slots", ()) if isinstance(value, str))
        if diagnostic_slot != slot and slot not in diagnostic_slots:
            continue
        code = getattr(diagnostic, "code", None)
        if isinstance(code, str) and code:
            codes.add(code)
    return sorted(codes)


def _authoring_slot_state(required: object, relative_paths: Sequence[str], diagnostic_codes: Sequence[str]) -> str:
    if not relative_paths:
        return "missing" if bool(required) else "empty"
    if diagnostic_codes:
        return "diagnostic"
    return "satisfied"


def _logical_authoring_slots(slots: object) -> tuple[tuple[dict[str, object], ...], ...]:
    groups: dict[str, list[dict[str, object]]] = {}
    for slot in slots if isinstance(slots, list) else ():
        if not isinstance(slot, Mapping):
            continue
        name = slot.get("name")
        match = slot.get("match")
        if isinstance(name, str) and isinstance(match, str):
            append_index_entry(groups, name, dict(slot))
    return tuple(tuple(groups[name]) for name in sorted(groups))


def _authoring_slot_loader(source_slots: tuple[Mapping[str, object], ...]) -> str | None:
    loaders = sorted({slot.get("kind") for slot in source_slots if isinstance(slot.get("kind"), str) and slot.get("kind")})
    return loaders[0] if len(loaders) == 1 else None


def _suggested_authoring_paths(
    root: Path,
    relative_root: str,
    source_slots: tuple[Mapping[str, object], ...],
) -> list[tuple[str, Path]]:
    paths: list[tuple[str, Path]] = []
    for slot in source_slots:
        match = slot.get("match")
        if not isinstance(match, str) or bool(slot.get("regex")) or _is_glob_match(match):
            continue
        path = PurePosixPath(match.replace("\\", "/"))
        if path.is_absolute() or ".." in path.parts:
            continue
        relative_path = f"{relative_root}/{path.as_posix()}" if relative_root else path.as_posix()
        paths.append((relative_path, root / Path(*path.parts)))
    return paths


def _authoring_slot_index(rows: object) -> dict[str, dict[str, list[int]]]:
    index: dict[str, dict[str, list[int]]] = {"loader": {}, "slot": {}, "status": {}}
    for row_index, row in enumerate(rows if isinstance(rows, list) else ()):
        if not isinstance(row, Mapping):
            continue
        _append_authoring_slot_index(index["slot"], row.get("slot"), row_index)
        _append_authoring_slot_index(index["loader"], row.get("loader"), row_index)
        _append_authoring_slot_index(index["status"], row.get("status"), row_index)
    return {name: {key: bucket[key] for key in sorted(bucket)} for name, bucket in index.items() if bucket}


def _append_authoring_slot_index(bucket: dict[str, list[int]], value: object, row_index: int) -> None:
    if isinstance(value, str) and value:
        append_index_entry(bucket, value, row_index)


def _authoring_owner_key(owner_kind: str) -> str:
    return "module_id" if owner_kind == "module" else "collection_id"


def _is_glob_match(value: str) -> bool:
    return any(char in value for char in "*?[")


def summary_view(result: BuildResult) -> dict[str, object]:
    """Return a build summary manifest payload.

    Args:
        result: Build result to inspect.

    Returns:
        JSON-safe `summary.json` manifest payload.
    """

    return dict(_summary_payload(result))


def manifests_view(result: BuildResult) -> dict[str, object]:
    """Return all build manifest payloads under one wrapper payload.

    Args:
        result: Build result to inspect.

    Returns:
        JSON-safe payload keyed by manifest file name.
    """

    payload: dict[str, object] = {
        "schema": MANIFESTS_SCHEMA,
        "project_id": result.project_id,
        "manifests": manifest_payloads(result),
    }
    if result.profile:
        payload["profile"] = result.profile
    return payload


def modules_view(
    result: BuildResult,
    *,
    family: str | None = None,
    module_id: str | None = None,
    collection_id: str | None = None,
    source_slot: str | None = None,
) -> dict[str, object]:
    """Return a filtered modules manifest payload.

    Args:
        result: Build result to inspect.
        family: Optional module family filter.
        module_id: Optional exact module id filter.
        collection_id: Optional collection id filter.
        source_slot: Optional source slot filter.

    Returns:
        JSON-safe `modules.json` payload with index rebuilt for returned rows.
    """

    payload = dict(manifest_payloads(result)["modules.json"])
    modules = _filter_module_rows(
        payload.get("modules"),
        family=family,
        module_id=module_id,
        collection_id=collection_id,
        source_slot=source_slot,
    )
    payload["modules"] = modules
    payload["index"] = module_index(modules)
    return payload


def collections_view(
    result: BuildResult,
    *,
    family: str | None = None,
    collection_id: str | None = None,
    module_id: str | None = None,
    source_slot: str | None = None,
) -> dict[str, object]:
    """Return a filtered collections manifest payload.

    Args:
        result: Build result to inspect.
        family: Optional collection family filter.
        collection_id: Optional exact collection id filter.
        module_id: Optional member module id filter.
        source_slot: Optional descriptor source slot filter.

    Returns:
        JSON-safe `collections.json` payload with index rebuilt for returned rows.
    """

    payload = dict(manifest_payloads(result)["collections.json"])
    collections = _filter_collection_rows(
        payload.get("collections"),
        family=family,
        collection_id=collection_id,
        module_id=module_id,
        source_slot=source_slot,
    )
    payload["collections"] = collections
    payload["index"] = collection_index(collections)
    return payload


def artifacts_view(
    result: BuildResult,
    *,
    artifact_type: str | None = None,
    target_root: str | None = None,
    owner: str | None = None,
    path: str | None = None,
    mode: str | None = None,
    module_id: str | None = None,
    collection_id: str | None = None,
) -> dict[str, object]:
    """Return a filtered artifacts manifest payload.

    Args:
        result: Build result to inspect.
        artifact_type: Optional artifact type filter.
        target_root: Optional artifact target root filter.
        owner: Optional exact artifact owner filter.
        path: Optional exact artifact path filter.
        mode: Optional artifact mode filter.
        module_id: Optional source or owner module filter.
        collection_id: Optional source or owner collection filter.

    Returns:
        JSON-safe `artifacts.json` payload with index rebuilt for returned rows.
    """

    payload = dict(manifest_payloads(result)["artifacts.json"])
    artifacts = _filter_artifact_rows(
        payload.get("artifacts"),
        artifact_type=artifact_type,
        target_root=target_root,
        owner=owner,
        path=path,
        mode=mode,
        module_id=module_id,
        collection_id=collection_id,
    )
    payload["artifacts"] = artifacts
    payload["index"] = artifact_index(artifacts)
    return payload


def localization_view(
    result: BuildResult,
    *,
    language: str | None = None,
    key: str | None = None,
    key_prefix: str | None = None,
    module_id: str | None = None,
    collection_id: str | None = None,
) -> dict[str, object]:
    """Return a filtered localization manifest payload.

    Args:
        result: Build result to inspect.
        language: Optional language id or alias filter.
        key: Optional exact localization key filter.
        key_prefix: Optional localization key prefix filter.
        module_id: Optional module id filter.
        collection_id: Optional collection id filter.

    Returns:
        JSON-safe `localization.json` payload with index rebuilt for returned rows.
    """

    payload = dict(manifest_payloads(result)["localization.json"])
    localization = _filter_localization_rows(
        payload.get("localization"),
        language=language,
        key=key,
        key_prefix=key_prefix,
        module_id=module_id,
        collection_id=collection_id,
    )
    payload["localization"] = localization
    payload["index"] = localization_index(localization)
    return payload


def assets_view(
    result: BuildResult,
    *,
    module_id: str | None = None,
    collection_id: str | None = None,
    family: str | None = None,
    slot: str | None = None,
    file_format: str | None = None,
) -> dict[str, object]:
    """Return a filtered assets manifest payload.

    Args:
        result: Build result to inspect.
        module_id: Optional module id filter.
        collection_id: Optional collection id filter.
        family: Optional source family filter.
        slot: Optional source slot filter.
        file_format: Optional lowercase asset format filter.

    Returns:
        JSON-safe `assets.json` payload with index rebuilt for returned rows.
    """

    payload = dict(manifest_payloads(result)["assets.json"])
    assets = _filter_asset_rows(
        payload.get("assets"),
        module_id=module_id,
        collection_id=collection_id,
        family=family,
        slot=slot,
        file_format=file_format,
    )
    payload["assets"] = assets
    payload["index"] = asset_index(assets)
    return payload


def sources_view(
    result: BuildResult,
    *,
    family: str | None = None,
    module_id: str | None = None,
    collection_id: str | None = None,
    slot: str | None = None,
    loader: str | None = None,
    status: str | None = None,
    owner_kind: str | None = None,
) -> dict[str, object]:
    """Return a filtered source inventory manifest payload.

    Args:
        result: Build result to inspect.
        family: Optional module or collection family filter.
        module_id: Optional module id filter.
        collection_id: Optional collection id filter.
        slot: Optional source slot filter.
        loader: Optional source loader filter.
        status: Optional source load status filter.
        owner_kind: Optional source owner kind filter, either `module` or
            `collection`.

    Returns:
        JSON-safe `sources.json` payload with index rebuilt for returned rows.

    Raises:
        ValueError: If owner_kind is not `module` or `collection`.
    """

    wanted_owner_kind = _source_owner_kind(owner_kind)
    payload = dict(manifest_payloads(result)["sources.json"])
    sources = _filter_source_rows(
        payload.get("sources"),
        family=family,
        module_id=module_id,
        collection_id=collection_id,
        slot=slot,
        loader=loader,
        status=status,
        owner_kind=wanted_owner_kind,
    )
    payload["sources"] = sources
    payload["index"] = source_inventory_index(sources)
    return payload


def sprites_view(
    result: BuildResult,
    *,
    module_id: str | None = None,
    collection_id: str | None = None,
    family: str | None = None,
    slot: str | None = None,
    name: str | None = None,
) -> dict[str, object]:
    """Return a filtered sprite manifest payload.

    Args:
        result: Build result to inspect.
        module_id: Optional source module id filter.
        collection_id: Optional source collection id filter.
        family: Optional source family filter.
        slot: Optional source slot filter.
        name: Optional exact sprite name filter.

    Returns:
        JSON-safe `sprites.json` payload with index rebuilt for returned rows.
    """

    payload = dict(manifest_payloads(result)["sprites.json"])
    sprites = _filter_sprite_rows(
        payload.get("sprites"),
        module_id=module_id,
        collection_id=collection_id,
        family=family,
        slot=slot,
        name=name,
    )
    payload["sprites"] = sprites
    payload["index"] = sprite_index(sprites)
    return payload


def diagnostics_view(
    result: BuildResult,
    *,
    severity: str | None = None,
    code: str | None = None,
    family: str | None = None,
    owner: str | None = None,
    target_root: str | None = None,
    module_id: str | None = None,
    collection_id: str | None = None,
    source_path: str | None = None,
    slot: str | None = None,
) -> dict[str, object]:
    """Return a filtered diagnostics manifest payload.

    Args:
        result: Build result to inspect.
        severity: Optional diagnostic severity filter.
        code: Optional exact diagnostic code filter.
        family: Optional family filter against row or resolved source context.
        owner: Optional exact diagnostic owner filter.
        target_root: Optional diagnostic artifact target root filter.
        module_id: Optional module id filter.
        collection_id: Optional collection id filter.
        source_path: Optional source path filter.
        slot: Optional source slot filter.

    Returns:
        JSON-safe `diagnostics.json` payload with indexes rebuilt for returned rows.
    """

    return diagnostics_manifest_view(
        manifest_payloads(result)["diagnostics.json"],
        severity=severity,
        code=code,
        family=family,
        owner=owner,
        target_root=target_root,
        module_id=module_id,
        collection_id=collection_id,
        source_path=source_path,
        slot=slot,
    )


def diagnostics_manifest_view(
    manifest: Mapping[str, object],
    *,
    severity: str | None = None,
    code: str | None = None,
    family: str | None = None,
    owner: str | None = None,
    target_root: str | None = None,
    module_id: str | None = None,
    collection_id: str | None = None,
    source_path: str | None = None,
    slot: str | None = None,
) -> dict[str, object]:
    """Filter one validated diagnostics manifest without rebuilding a project.

    Args:
        manifest: Previously validated `diagnostics.json` payload.
        severity: Optional diagnostic severity filter.
        code: Optional exact diagnostic code filter.
        family: Optional module family filter.
        owner: Optional exact diagnostic owner filter.
        target_root: Optional diagnostic artifact target root filter.
        module_id: Optional module id filter.
        collection_id: Optional collection id filter.
        source_path: Optional source path filter.
        slot: Optional source slot filter.

    Returns:
        Detached diagnostics payload with indexes rebuilt for returned rows.
    """

    payload = dict(manifest)
    diagnostics = _filter_diagnostic_rows(
        payload.get("diagnostics"),
        severity=severity,
        code=code,
        family=family,
        owner=owner,
        target_root=target_root,
        module_id=module_id,
        collection_id=collection_id,
        source_path=source_path,
        slot=slot,
    )
    payload["diagnostics"] = diagnostics
    payload["index"] = diagnostic_index(diagnostics)
    payload["family_index"] = diagnostic_family_index(diagnostics)
    return payload


def source_map_view(
    result: BuildResult,
    *,
    module_id: str | None = None,
    collection_id: str | None = None,
    family: str | None = None,
    slot: str | None = None,
    artifact_type: str | None = None,
    target_root: str | None = None,
) -> dict[str, object]:
    """Return a filtered source-map manifest payload.

    Args:
        result: Build result to inspect.
        module_id: Optional module id source filter.
        collection_id: Optional collection id source filter.
        family: Optional module or collection family source filter.
        slot: Optional source slot filter.
        artifact_type: Optional artifact type filter.
        target_root: Optional artifact target root filter.

    Returns:
        JSON-safe `source-map.json` payload with index rebuilt for returned rows.
    """

    payload = dict(manifest_payloads(result)["source-map.json"])
    rows = _filter_source_map_rows(
        payload.get("source_map"),
        module_id=module_id,
        collection_id=collection_id,
        family=family,
        slot=slot,
        artifact_type=artifact_type,
        target_root=target_root,
    )
    payload["source_map"] = rows
    payload["index"] = source_map_index(rows)
    return payload


def dependencies_view(
    result: BuildResult,
    *,
    source: str | None = None,
    target: str | None = None,
    kind: str | None = None,
    module_id: str | None = None,
) -> dict[str, object]:
    """Return a filtered dependencies manifest payload.

    Args:
        result: Build result to inspect.
        source: Optional exact dependency source filter.
        target: Optional exact dependency target filter.
        kind: Optional dependency kind filter.
        module_id: Optional module id shorthand for `source="module:<id>"`.

    Returns:
        JSON-safe `dependencies.json` payload with index rebuilt for returned rows.
    """

    payload = dict(manifest_payloads(result)["dependencies.json"])
    dependencies = _filter_dependency_rows(
        payload.get("dependencies"),
        source=source,
        target=target,
        kind=kind,
        module_id=module_id,
    )
    payload["dependencies"] = dependencies
    payload["index"] = dependency_index(dependencies)
    return payload


def _filter_localization_rows(
    rows: object,
    *,
    language: str | None = None,
    key: str | None = None,
    key_prefix: str | None = None,
    module_id: str | None = None,
    collection_id: str | None = None,
) -> list[dict[str, object]]:
    wanted_language = canonical_language(language) if language else None
    filtered: list[dict[str, object]] = []
    for row in rows if isinstance(rows, list) else ():
        if not isinstance(row, dict):
            continue
        row_key = row.get("key")
        if wanted_language and row.get("language") != wanted_language:
            continue
        if key and row_key != key:
            continue
        if key_prefix and (not isinstance(row_key, str) or not row_key.startswith(key_prefix)):
            continue
        if module_id and row.get("module_id") != module_id:
            continue
        if collection_id and row.get("collection_id") != collection_id:
            continue
        filtered.append(dict(row))
    return filtered


def _filter_module_rows(
    rows: object,
    *,
    family: str | None = None,
    module_id: str | None = None,
    collection_id: str | None = None,
    source_slot: str | None = None,
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
        if source_slot and not _row_has_slot(row, source_slot):
            continue
        filtered.append(dict(row))
    return filtered


def _filter_collection_rows(
    rows: object,
    *,
    family: str | None = None,
    collection_id: str | None = None,
    module_id: str | None = None,
    source_slot: str | None = None,
) -> list[dict[str, object]]:
    filtered: list[dict[str, object]] = []
    for row in rows if isinstance(rows, list) else ():
        if not isinstance(row, dict):
            continue
        if family and row.get("family") != family:
            continue
        if collection_id and row.get("collection_id") != collection_id:
            continue
        if module_id and not _collection_row_has_module(row, module_id):
            continue
        if source_slot and not _row_has_slot(row, source_slot):
            continue
        filtered.append(dict(row))
    return filtered


def _collection_row_has_module(row: Mapping[object, object], module_id: str) -> bool:
    module_ids = row.get("module_ids")
    return isinstance(module_ids, list) and module_id in module_ids


def _row_has_slot(row: Mapping[object, object], slot: str) -> bool:
    slots = row.get("source_slots")
    return isinstance(slots, dict) and slot in slots


def _filter_artifact_rows(
    rows: object,
    *,
    artifact_type: str | None = None,
    target_root: str | None = None,
    owner: str | None = None,
    path: str | None = None,
    mode: str | None = None,
    module_id: str | None = None,
    collection_id: str | None = None,
) -> list[dict[str, object]]:
    filtered: list[dict[str, object]] = []
    for row in rows if isinstance(rows, list) else ():
        if not isinstance(row, dict):
            continue
        if artifact_type and row.get("type") != artifact_type:
            continue
        if target_root and row.get("target_root") != target_root:
            continue
        if path and row.get("path") != path:
            continue
        if mode and row.get("mode") != mode:
            continue
        if not _artifact_row_context_matches(row, owner=owner, module_id=module_id, collection_id=collection_id):
            continue
        filtered.append(dict(row))
    return filtered


def _artifact_row_context_matches(
    row: Mapping[object, object],
    *,
    owner: str | None = None,
    module_id: str | None = None,
    collection_id: str | None = None,
) -> bool:
    if owner and row.get("owner") != owner:
        return False
    if module_id and module_id not in artifact_module_ids(row):
        return False
    if collection_id and collection_id not in artifact_collection_ids(row):
        return False
    return True


def _filter_asset_rows(
    rows: object,
    *,
    module_id: str | None = None,
    collection_id: str | None = None,
    family: str | None = None,
    slot: str | None = None,
    file_format: str | None = None,
) -> list[dict[str, object]]:
    wanted_format = file_format.lower().lstrip(".") if file_format else None
    filtered: list[dict[str, object]] = []
    for row in rows if isinstance(rows, list) else ():
        if not isinstance(row, dict):
            continue
        if module_id and row.get("module_id") != module_id:
            continue
        if collection_id and row.get("collection_id") != collection_id:
            continue
        if family and row.get("family") != family:
            continue
        if slot and row.get("slot") != slot:
            continue
        if wanted_format and row.get("format") != wanted_format:
            continue
        filtered.append(dict(row))
    return filtered


def _filter_source_rows(
    rows: object,
    *,
    family: str | None = None,
    module_id: str | None = None,
    collection_id: str | None = None,
    slot: str | None = None,
    loader: str | None = None,
    status: str | None = None,
    owner_kind: str | None = None,
) -> list[dict[str, object]]:
    filtered: list[dict[str, object]] = []
    for row in rows if isinstance(rows, list) else ():
        if not isinstance(row, dict):
            continue
        if owner_kind and row.get("owner_kind") != owner_kind:
            continue
        if family and row.get("family") != family:
            continue
        if module_id and row.get("module_id") != module_id:
            continue
        if collection_id and row.get("collection_id") != collection_id:
            continue
        if slot and row.get("slot") != slot:
            continue
        if loader and row.get("loader") != loader:
            continue
        if status and row.get("status") != status:
            continue
        filtered.append(dict(row))
    return filtered


def _source_owner_kind(owner_kind: str | None) -> str | None:
    if owner_kind is None:
        return None
    text = owner_kind.strip().lower()
    if text in {"module", "collection"}:
        return text
    raise ValueError(f"Unsupported source owner kind: {owner_kind!r}. Expected 'module' or 'collection'.")


def _filter_sprite_rows(
    rows: object,
    *,
    module_id: str | None = None,
    collection_id: str | None = None,
    family: str | None = None,
    slot: str | None = None,
    name: str | None = None,
) -> list[dict[str, object]]:
    filtered: list[dict[str, object]] = []
    for row in rows if isinstance(rows, list) else ():
        if not isinstance(row, dict):
            continue
        if module_id and row.get("module_id") != module_id:
            continue
        if collection_id and row.get("collection_id") != collection_id:
            continue
        if family and row.get("family") != family:
            continue
        if slot and row.get("slot") != slot:
            continue
        if name and row.get("name") != name:
            continue
        filtered.append(dict(row))
    return filtered


def _filter_diagnostic_rows(
    rows: object,
    *,
    severity: str | None = None,
    code: str | None = None,
    family: str | None = None,
    owner: str | None = None,
    target_root: str | None = None,
    module_id: str | None = None,
    collection_id: str | None = None,
    source_path: str | None = None,
    slot: str | None = None,
) -> list[dict[str, object]]:
    filtered: list[dict[str, object]] = []
    for row in rows if isinstance(rows, list) else ():
        if not isinstance(row, dict):
            continue
        if severity and row.get("severity") != severity:
            continue
        if code and row.get("code") != code:
            continue
        if family and not _diagnostic_row_matches(row, "family", family):
            continue
        if not _diagnostic_row_matches(row, "owner", owner):
            continue
        if target_root and row.get("target_root") != target_root:
            continue
        if not _diagnostic_row_matches(row, "module_id", module_id):
            continue
        if not _diagnostic_row_matches(row, "collection_id", collection_id):
            continue
        if not _diagnostic_row_matches(row, "source_path", source_path, source_key="path"):
            continue
        if not _diagnostic_row_matches(row, "slot", slot):
            continue
        filtered.append(dict(row))
    return filtered


def _diagnostic_row_matches(
    row: Mapping[object, object],
    key: str,
    value: str | None,
    *,
    source_key: str | None = None,
) -> bool:
    if value is None:
        return True
    if key == "slot" and _row_values_contain(row, key="slots", value=value):
        return True
    if key == "owner" and _row_values_contain(row, key="owners", value=value):
        return True
    return row.get(key) == value or _diagnostic_source_value(row, source_key or key) == value


def _row_values_contain(row: Mapping[object, object], *, key: str, value: str) -> bool:
    values = row.get(key)
    return isinstance(values, (list, tuple)) and value in values


def _diagnostic_source_value(row: Mapping[object, object], key: str) -> object:
    source = row.get("source")
    return source.get(key) if isinstance(source, dict) else None


def _filter_source_map_rows(
    rows: object,
    *,
    module_id: str | None = None,
    collection_id: str | None = None,
    family: str | None = None,
    slot: str | None = None,
    artifact_type: str | None = None,
    target_root: str | None = None,
) -> list[dict[str, object]]:
    filtered: list[dict[str, object]] = []
    for row in rows if isinstance(rows, list) else ():
        if not isinstance(row, dict):
            continue
        if artifact_type and row.get("type") != artifact_type:
            continue
        if target_root and row.get("target_root") != target_root:
            continue
        if (module_id or collection_id or family or slot) and not _source_map_row_has_source(
            row,
            module_id=module_id,
            collection_id=collection_id,
            family=family,
            slot=slot,
        ):
            continue
        filtered.append(dict(row))
    return filtered


def _source_map_row_has_source(
    row: Mapping[object, object],
    *,
    module_id: str | None = None,
    collection_id: str | None = None,
    family: str | None = None,
    slot: str | None = None,
) -> bool:
    sources = row.get("sources")
    for source in sources if isinstance(sources, list) else ():
        if not isinstance(source, dict):
            continue
        if module_id and source.get("module_id") != module_id:
            continue
        if collection_id and source.get("collection_id") != collection_id:
            continue
        if family and source.get("family") != family:
            continue
        if slot and source.get("slot") != slot:
            continue
        return True
    return False


def _filter_dependency_rows(
    rows: object,
    *,
    source: str | None = None,
    target: str | None = None,
    kind: str | None = None,
    module_id: str | None = None,
) -> list[dict[str, object]]:
    wanted_source = _dependency_source_filter(source, module_id)
    filtered: list[dict[str, object]] = []
    for row in rows if isinstance(rows, list) else ():
        if not isinstance(row, dict):
            continue
        if wanted_source and row.get("source") != wanted_source:
            continue
        if target and row.get("target") != target:
            continue
        if kind and row.get("kind") != kind:
            continue
        filtered.append(dict(row))
    return filtered


def _dependency_source_filter(source: str | None, module_id: str | None) -> str | None:
    value = source or module_id
    if not value:
        return None
    if ":" in value:
        return value
    return f"module:{value}"
