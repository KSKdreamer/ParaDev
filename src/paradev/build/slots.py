"""Generic source slot matching."""

from __future__ import annotations

import fnmatch
import os
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from .records import Diagnostic

IMAGE_SLOT_FORMAT_PRIORITY = {
    ".png": 0,
    ".jpg": 1,
    ".jpeg": 1,
    ".webp": 2,
    ".dds": 3,
    ".tga": 4,
    ".bmp": 5,
}


@dataclass(frozen=True, slots=True)
class Slot:
    """A family-declared source and authoring resource slot.

    ``authoring_path`` is an optional module-relative destination template for
    adding a new ``copy`` resource. Build discovery continues to use ``match``
    as the source of truth; authoring surfaces render only the safe
    ``extension``, ``filename``, ``object_id``, and ``stem`` placeholders, then
    require the rendered path to satisfy this slot before writing it.
    """

    name: str
    match: str
    required: bool = False
    many: bool = False
    regex: bool = False
    kind: str | None = None
    shared: bool = False
    authoring_path: str | None = None


@dataclass(frozen=True, slots=True)
class SlotMatchResult:
    """Matched source slots and diagnostics."""

    source_slots: dict[str, tuple[str, ...]]
    diagnostics: tuple[Diagnostic, ...] = ()


def match_slots(root: str | Path, slots: tuple[Slot, ...], *, module_id: str | None = None) -> SlotMatchResult:
    """Match source slots against a module root.

    Args:
        root: Module source root.
        slots: Slot declarations.
        module_id: Optional module id for diagnostics.

    Returns:
        Matched relative POSIX paths and diagnostics.
    """

    return match_slot_paths(_relative_files(Path(root)), slots, module_id=module_id)


def match_slot_paths(paths: tuple[str, ...], slots: tuple[Slot, ...], *, module_id: str | None = None) -> SlotMatchResult:
    """Match source slots against an in-memory set of relative file paths.

    Args:
        paths: Relative POSIX file paths available under a prospective module root.
        slots: Slot declarations to validate.
        module_id: Optional module id for diagnostics.

    Returns:
        Matched relative POSIX paths and diagnostics.
    """

    files = tuple(sorted(set(paths)))
    matched: dict[str, set[str]] = {}
    allow_many: dict[str, bool] = {}
    allow_shared: dict[str, bool] = {}
    diagnostics: list[Diagnostic] = []

    for slot in sorted(slots, key=lambda item: item.name):
        allow_many[slot.name] = allow_many.get(slot.name, False) or slot.many
        allow_shared[slot.name] = allow_shared.get(slot.name, False) or slot.shared
        pattern: re.Pattern[str] | None = None
        if slot.regex:
            try:
                pattern = re.compile(slot.match)
            except re.error as error:
                diagnostics.append(
                    Diagnostic(
                        code="slot.invalid_regex",
                        message=f"Slot {slot.name!r} match {slot.match!r} must be a valid regex: {error}.",
                        module_id=module_id,
                        slot=slot.name,
                    )
                )
                continue
        if slot_match_escapes_root(slot.match, regex=slot.regex):
            diagnostics.append(
                Diagnostic(
                    code="slot.invalid_match",
                    message=f"Slot {slot.name!r} match {slot.match!r} must be relative and stay under the source root.",
                    module_id=module_id,
                    slot=slot.name,
                )
            )
            continue
        matched_paths = _match_one(files, slot, pattern=pattern)
        if not matched_paths:
            if slot.required:
                diagnostics.append(
                    Diagnostic(
                        code="slot.missing_required",
                        message=f"Required slot {slot.name!r} did not match {slot.match!r}.",
                        module_id=module_id,
                        slot=slot.name,
                    )
                )
            continue
        if not slot.many and len(matched_paths) > 1:
            diagnostics.append(
                Diagnostic(
                    code="slot.multiple_matches",
                    message=f"Slot {slot.name!r} matched {len(matched_paths)} files but many=False.",
                    module_id=module_id,
                    slot=slot.name,
                )
            )
            matched_paths = matched_paths[:1]
        matched.setdefault(slot.name, set()).update(matched_paths)

    source_slots = _final_source_slots(matched, allow_many=allow_many, diagnostics=diagnostics, module_id=module_id)
    for path, names in _source_ownership(source_slots).items():
        if len(names) > 1 and not _source_shared(names, allow_shared):
            slots = tuple(sorted(names))
            diagnostics.append(
                Diagnostic(
                    code="slot.source_collision",
                    message=f"Source file {path} matched multiple slots: {', '.join(slots)}.",
                    module_id=module_id,
                    slot=slots[0],
                    slots=slots,
                    source_path=path,
                )
            )

    return SlotMatchResult(
        source_slots=source_slots,
        diagnostics=tuple(diagnostics),
    )


def _final_source_slots(
    matched: dict[str, set[str]],
    *,
    allow_many: dict[str, bool],
    diagnostics: list[Diagnostic],
    module_id: str | None,
) -> dict[str, tuple[str, ...]]:
    source_slots: dict[str, tuple[str, ...]] = {}
    for name, paths in sorted(matched.items()):
        ordered_paths = tuple(sorted(paths, key=_source_slot_order_key))
        if not allow_many.get(name, False) and len(ordered_paths) > 1:
            diagnostics.append(
                Diagnostic(
                    code="slot.multiple_matches",
                    message=f"Slot {name!r} matched {len(ordered_paths)} files but many=False.",
                    module_id=module_id,
                    slot=name,
                )
            )
            ordered_paths = ordered_paths[:1]
        source_slots[name] = ordered_paths
    return source_slots


def _source_ownership(source_slots: dict[str, tuple[str, ...]]) -> dict[str, set[str]]:
    ownership: dict[str, set[str]] = {}
    for slot, paths in sorted(source_slots.items()):
        for path in paths:
            ownership.setdefault(path, set()).add(slot)
    return dict(sorted(ownership.items()))


def _source_shared(names: set[str], allow_shared: dict[str, bool]) -> bool:
    return all(allow_shared.get(name, False) for name in names)


def _relative_files(root: Path) -> tuple[str, ...]:
    if not root.is_dir():
        return ()
    paths: list[str] = []
    for directory, _directories, files in os.walk(root, onerror=_raise_walk_error):
        directory_path = Path(directory)
        relative_directory = directory_path.relative_to(root)
        paths.extend((relative_directory / name).as_posix() for name in files if (directory_path / name).is_file())
    return tuple(sorted(paths))


def _raise_walk_error(error: OSError) -> None:
    """Keep source discovery fail-closed when a directory cannot be read."""

    raise error


def _match_one(files: tuple[str, ...], slot: Slot, *, pattern: re.Pattern[str] | None = None) -> list[str]:
    if slot.regex:
        compiled = pattern or re.compile(slot.match)
        return sorted(
            (path for path in files if compiled.search(path)),
            key=_source_slot_order_key,
        )
    if _is_glob(slot.match):
        return sorted(
            (path for path in files if _glob_match(path, slot.match)),
            key=_source_slot_order_key,
        )
    return [slot.match] if slot.match in files else []


def _glob_match(path: str, pattern: str) -> bool:
    if fnmatch.fnmatchcase(path, pattern):
        return True
    if pattern.startswith("**/"):
        return fnmatch.fnmatchcase(path, pattern[3:])
    return False


def _is_glob(value: str) -> bool:
    return any(char in value for char in "*?[")


def slot_match_escapes_root(match: str, *, regex: bool = False) -> bool:
    """Return whether a non-regex slot match can escape its source root."""

    if regex:
        return False
    path = PurePosixPath(match.replace("\\", "/"))
    return path.is_absolute() or ".." in path.parts


def _source_slot_order_key(path: str) -> tuple[int, str]:
    suffix = PurePosixPath(path).suffix.lower()
    return (
        IMAGE_SLOT_FORMAT_PRIORITY.get(suffix, len(IMAGE_SLOT_FORMAT_PRIORITY)),
        path,
    )
