"""Generic source loaders for matched slots."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from struct import unpack_from
from typing import Any

from heavenbase.utils import dmerge, load_txt, sha256hash
from yaml import YAMLError
from yaml import load as load_yaml_text

try:
    from yaml import CSafeLoader as _MetadataYamlLoader
except ImportError:  # pragma: no cover - exercised on PyYAML builds without LibYAML.
    from yaml import SafeLoader as _MetadataYamlLoader

from paradev.localization._source import parse_source
from paradev.pdx import PDXBlock, PDXDiagnostic, PDXParseError

from .records import Collection, Diagnostic, Module
from .slots import Slot

METADATA_KEYS = {
    "type",
    "title",
    "tags",
    "comment",
    "collection",
    "owner",
    "priority",
    "game_id",
    "requires",
    "after",
    "inactive",
    "members",
    "settings",
}
HIDDEN_METADATA_PATH = Path(".paradev/meta.yaml")
DEFAULT_PDX_SLOTS = ("def", "pdx", "extra", "script", "gui", "gfx", "asset")
DEFAULT_LOC_SLOTS = ("loc", "loc_yml", "localization", "localisation")
DEFAULT_COPY_SLOTS = ("copy", "icon", "portrait", "picture", "assets")


def content_sha256(payload: bytes) -> str:
    """Return the exact SHA-256 digest of binary build content.

    Args:
        payload (bytes): Exact bytes that a loader or writer will publish.

    Returns:
        str: Lowercase hexadecimal SHA-256 digest of `payload`.
    """

    return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True, slots=True)
class MetadataLoadResult:
    """Loaded module metadata and diagnostics."""

    metadata: dict[str, Any]
    diagnostics: tuple[Diagnostic, ...] = ()


@dataclass(frozen=True, slots=True)
class CollectionLoadResult:
    """Loaded collection descriptor and diagnostics."""

    collection: Collection
    diagnostics: tuple[Diagnostic, ...] = ()


@dataclass(frozen=True, slots=True)
class PDXBlockSource:
    """One parsed PDX source file."""

    slot: str
    path: str
    block: PDXBlock


@dataclass(frozen=True, slots=True)
class PDXLoadResult:
    """Loaded PDX sources and diagnostics."""

    sources: tuple[PDXBlockSource, ...]
    diagnostics: tuple[Diagnostic, ...] = ()


@dataclass(frozen=True, slots=True)
class LocalizationEntry:
    """One localization key in a source `.loc` file."""

    key: str
    language: str
    text: str
    source_path: str
    module_id: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        """Return a JSON-safe localization entry."""

        return {
            "key": self.key,
            "language": self.language,
            "text": self.text,
            "source_path": self.source_path,
            "module_id": self.module_id,
        }


@dataclass(frozen=True, slots=True)
class LocalizationLoadResult:
    """Loaded localization entries and diagnostics."""

    entries: tuple[LocalizationEntry, ...]
    diagnostics: tuple[Diagnostic, ...] = ()


@dataclass(frozen=True, slots=True)
class CopySource:
    """One static copy source with hash metadata."""

    slot: str
    path: str
    output_path: str
    sha256: str
    size: int
    content_sha256: str | None = None
    media_type: str | None = None
    format: str | None = None
    width: int | None = None
    height: int | None = None

    def to_dict(self) -> dict[str, str | int]:
        """Return a JSON-safe copy source view."""

        data: dict[str, str | int] = {
            "slot": self.slot,
            "path": self.path,
            "output_path": self.output_path,
            "sha256": self.sha256,
            "size": self.size,
        }
        if self.content_sha256:
            data["content_sha256"] = self.content_sha256
        if self.media_type:
            data["media_type"] = self.media_type
        if self.format:
            data["format"] = self.format
        if self.width is not None:
            data["width"] = self.width
        if self.height is not None:
            data["height"] = self.height
        return data


@dataclass(frozen=True, slots=True)
class CopyLoadResult:
    """Loaded static copy sources and diagnostics."""

    sources: tuple[CopySource, ...]
    diagnostics: tuple[Diagnostic, ...] = ()


@dataclass(frozen=True, slots=True)
class _MetadataReadResult:
    data: dict[str, Any]
    invalid_yaml: bool = False
    invalid_mapping: bool = False
    unreadable_error: str | None = None


@dataclass(frozen=True, slots=True)
class ModuleSourceBundle:
    """Normalized loader output for one source module."""

    root: str
    source_slots: dict[str, tuple[str, ...]]
    metadata: dict[str, Any]
    pdx_sources: tuple[PDXBlockSource, ...] = ()
    loc_entries: tuple[LocalizationEntry, ...] = ()
    copy_sources: tuple[CopySource, ...] = ()
    diagnostics: tuple[Diagnostic, ...] = ()
    module_id: str | None = None

    def to_module(self, *, family: str | None = None, collection_id: str | None = None) -> Module:
        """Return the public `Module` record for this source bundle."""

        family_id = family or _metadata_text(self.metadata, "type")
        if not family_id:
            raise ValueError("Module source bundle cannot become a Module without a family or metadata type.")
        object_id = _metadata_text(self.metadata, "object_id") or Path(self.root).name
        module_id = self.module_id or f"{family_id}/{object_id}"
        return Module(
            module_id=module_id,
            family=family_id,
            root=self.root,
            source_slots=self.source_slots,
            collection_id=collection_id if collection_id is not None else _metadata_text(self.metadata, "collection"),
            metadata=self.metadata,
            payload=self,
        )


@dataclass(frozen=True, slots=True)
class CollectionSourceBundle:
    """Normalized loader output for one collection descriptor root."""

    root: str
    metadata: dict[str, Any]
    source_slots: dict[str, tuple[str, ...]] = field(default_factory=dict)
    pdx_sources: tuple[PDXBlockSource, ...] = ()
    loc_entries: tuple[LocalizationEntry, ...] = ()
    copy_sources: tuple[CopySource, ...] = ()
    diagnostics: tuple[Diagnostic, ...] = ()
    collection_id: str | None = None
    family: str | None = None

    def to_collection(self, *, family: str | None = None, collection_id: str | None = None) -> Collection:
        """Return the public `Collection` record for this source bundle."""

        family_id = family or self.family
        object_id = collection_id or self.collection_id or _metadata_text(self.metadata, "object_id") or Path(self.root).name
        if not family_id:
            raise ValueError("Collection source bundle cannot become a Collection without a family.")
        return Collection(
            collection_id=object_id,
            family=family_id,
            module_ids=_collection_member_ids(self.metadata.get("members"), family=family_id),
            source_slots=self.source_slots,
            metadata=self.metadata,
            payload=self,
        )


def load_metadata(
    root: str | Path,
    *,
    inferred_type: str | None = None,
    module_id: str | None = None,
    metadata_keys: Sequence[str] = (),
    strict_metadata: bool = False,
) -> MetadataLoadResult:
    """Load `meta.yaml` and infer folder identity.

    Args:
        root: Module source root.
        inferred_type: Optional module type inferred from typed ancestry.
        module_id: Optional module id for diagnostics.
        metadata_keys: Additional family-owned top-level metadata keys.
        strict_metadata: Whether unknown metadata keys should be blocking
            errors instead of loose-mode warnings.

    Returns:
        Metadata payload with inferred `object_id` and diagnostics.
    """

    base = Path(root)
    path = base / "meta.yaml"
    hidden_path = base / HIDDEN_METADATA_PATH
    hidden_read = _read_metadata(hidden_path)
    read = _read_metadata(path)
    raw = dmerge([hidden_read.data, read.data])
    object_id, note = _folder_identity(base.name)
    metadata: dict[str, Any] = {"object_id": object_id}
    if note:
        metadata["note"] = note
    if inferred_type:
        metadata["type"] = inferred_type
    metadata.update(raw)
    if note and "title" not in raw:
        metadata["title"] = note

    diagnostics: list[Diagnostic] = []
    for layer_path, layer_read in (
        (HIDDEN_METADATA_PATH.as_posix(), hidden_read),
        ("meta.yaml", read),
    ):
        diagnostics.extend(
            _module_metadata_read_diagnostics(
                layer_read,
                module_id=module_id,
                source_path=layer_path,
            )
        )
    if inferred_type and raw.get("type") and raw["type"] != inferred_type:
        diagnostics.append(
            Diagnostic(
                code="metadata.type_mismatch",
                message=f"meta.yaml type {raw['type']!r} does not match inferred type {inferred_type!r}.",
                module_id=module_id,
                source_path="meta.yaml",
            )
        )
    if "inactive" in raw and not isinstance(raw["inactive"], bool):
        diagnostics.append(
            Diagnostic(
                code="metadata.invalid_inactive",
                message="meta.yaml inactive must be true or false.",
                module_id=module_id,
                source_path="meta.yaml",
            )
        )
    allowed_keys = {*METADATA_KEYS, *metadata_keys}
    for key in sorted(set(raw) - allowed_keys):
        diagnostics.append(
            Diagnostic(
                code="metadata.unknown_key",
                message=f"Unknown metadata key {key!r}.",
                severity=_metadata_unknown_key_severity(strict_metadata),
                module_id=module_id,
                source_path="meta.yaml",
            )
        )
    return MetadataLoadResult(metadata=metadata, diagnostics=tuple(diagnostics))


def load_collection_metadata(
    root: str | Path,
    *,
    family: str,
    collection_id: str | None = None,
    metadata_keys: Sequence[str] = (),
    strict_metadata: bool = False,
) -> CollectionLoadResult:
    """Load a collection descriptor from `meta.yaml` or `collection.yaml`.

    Args:
        root: Collection descriptor root.
        family: Collection family inferred from typed ancestry.
        collection_id: Optional collection id override.
        metadata_keys: Additional family-owned top-level metadata keys.
        strict_metadata: Whether unknown metadata keys should be blocking
            errors instead of loose-mode warnings.

    Returns:
        Collection descriptor and diagnostics.
    """

    base = Path(root)
    path = _collection_metadata_path(base)
    hidden_path = base / HIDDEN_METADATA_PATH
    hidden_read = _read_metadata(hidden_path)
    read = _read_metadata(path)
    raw = dmerge([hidden_read.data, read.data])
    object_id, note = _folder_identity(collection_id or base.name)
    metadata: dict[str, Any] = {"object_id": object_id}
    if note:
        metadata["note"] = note
    metadata.update(raw)
    if note and "title" not in raw:
        metadata["title"] = note

    diagnostics: list[Diagnostic] = []
    for layer_path, layer_read in (
        (HIDDEN_METADATA_PATH.as_posix(), hidden_read),
        (path.name, read),
    ):
        diagnostics.extend(
            _collection_metadata_read_diagnostics(
                layer_read,
                collection_id=object_id,
                source_path=layer_path,
            )
        )
    allowed_keys = {*METADATA_KEYS, *metadata_keys}
    for key in sorted(set(raw) - allowed_keys):
        diagnostics.append(
            Diagnostic(
                code="collection_metadata.unknown_key",
                message=f"Unknown collection metadata key {key!r}.",
                severity=_metadata_unknown_key_severity(strict_metadata),
                collection_id=object_id,
                source_path=path.name,
            )
        )
    member_ids, member_diagnostics = _collection_members(
        metadata.get("members"),
        family=family,
        collection_id=object_id,
        source_path=path.name,
    )
    diagnostics.extend(member_diagnostics)
    return CollectionLoadResult(
        collection=Collection(
            collection_id=object_id,
            family=family,
            module_ids=member_ids,
            metadata=metadata,
        ),
        diagnostics=tuple(diagnostics),
    )


def _collection_member_ids(value: object, *, family: str) -> tuple[str, ...]:
    """Normalize ordered collection members from concise or qualified ids."""

    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return ()
    members: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            continue
        member = item.strip()
        members.append(member if "/" in member else f"{family}/{member}")
    return tuple(dict.fromkeys(members))


def _collection_members(
    value: object,
    *,
    family: str,
    collection_id: str,
    source_path: str,
) -> tuple[tuple[str, ...], tuple[Diagnostic, ...]]:
    if value is None:
        return (), ()
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return (
            (),
            (
                Diagnostic(
                    code="collection_metadata.invalid_members",
                    message="Collection members must be an ordered YAML list of module ids.",
                    collection_id=collection_id,
                    source_path=source_path,
                ),
            ),
        )
    members: list[str] = []
    diagnostics: list[Diagnostic] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            diagnostics.append(
                Diagnostic(
                    code="collection_metadata.invalid_member",
                    message=f"Collection members[{index}] must be a non-empty module id.",
                    collection_id=collection_id,
                    source_path=source_path,
                )
            )
            continue
        member = item.strip()
        qualified = member if "/" in member else f"{family}/{member}"
        member_family, separator, object_id = qualified.partition("/")
        if not separator or member_family != family or not object_id or "/" in object_id:
            diagnostics.append(
                Diagnostic(
                    code="collection_metadata.invalid_member",
                    message=f"Collection members[{index}] {member!r} must identify one {family!r} module.",
                    collection_id=collection_id,
                    source_path=source_path,
                )
            )
            continue
        if qualified in seen:
            diagnostics.append(
                Diagnostic(
                    code="collection_metadata.duplicate_member",
                    message=f"Collection member {qualified!r} is listed more than once.",
                    collection_id=collection_id,
                    source_path=source_path,
                )
            )
            continue
        seen.add(qualified)
        members.append(qualified)
    return tuple(members), tuple(diagnostics)


def load_collection_sources(
    root: str | Path,
    *,
    family: str,
    collection_id: str | None = None,
    source_slots: Mapping[str, Sequence[str | Path]] | None = None,
    slots: Sequence[Slot] = (),
    metadata_keys: Sequence[str] = (),
    strict_metadata: bool = False,
) -> CollectionLoadResult:
    """Load generic source records for one collection descriptor root.

    Args:
        root: Collection descriptor root.
        family: Collection family inferred from typed ancestry.
        collection_id: Optional collection id override.
        source_slots: Optional matched descriptor slot names to relative paths.
        slots: Optional slot declarations with explicit loader roles.
        metadata_keys: Additional family-owned top-level metadata keys.
        strict_metadata: Whether unknown descriptor metadata keys should be
            blocking errors instead of loose-mode warnings.

    Returns:
        Collection descriptor with parsed collection-owned PDX and localization
        sources plus static copy source metadata.
    """

    base = Path(root)
    metadata = load_collection_metadata(
        base,
        family=family,
        collection_id=collection_id,
        metadata_keys=metadata_keys,
        strict_metadata=strict_metadata,
    )
    normalized_slots = _normalized_source_slots(source_slots) if source_slots is not None else _default_collection_source_slots(base)
    pdx = load_pdx_sources(
        base,
        _slot_subset(normalized_slots, _loader_slot_names(("def",), slots, "pdx")),
        collection_id=metadata.collection.collection_id,
    )
    loc = load_loc_sources(
        base,
        _slot_subset(normalized_slots, _loader_slot_names(("loc",), slots, "loc")),
        collection_id=metadata.collection.collection_id,
    )
    copy = load_copy_sources(
        base,
        _slot_subset(normalized_slots, _loader_slot_names((), slots, "copy")),
        collection_id=metadata.collection.collection_id,
    )
    bundle = CollectionSourceBundle(
        root=str(base),
        metadata=dict(metadata.collection.metadata),
        source_slots=normalized_slots,
        pdx_sources=pdx.sources,
        loc_entries=loc.entries,
        copy_sources=copy.sources,
        diagnostics=(*metadata.diagnostics, *pdx.diagnostics, *loc.diagnostics, *copy.diagnostics),
        collection_id=metadata.collection.collection_id,
        family=family,
    )
    return CollectionLoadResult(collection=bundle.to_collection(), diagnostics=bundle.diagnostics)


def load_pdx_sources(
    root: str | Path,
    source_slots: dict[str, tuple[str, ...]],
    *,
    module_id: str | None = None,
    collection_id: str | None = None,
) -> PDXLoadResult:
    """Parse matched PDX slot files into `PDXBlock` sources.

    Args:
        root: Module source root.
        source_slots: Slot name to relative source paths.
        module_id: Optional module id for diagnostics.
        collection_id: Optional collection id for diagnostics.

    Returns:
        Parsed PDX sources and diagnostics.
    """

    base = Path(root)
    sources: list[PDXBlockSource] = []
    diagnostics: list[Diagnostic] = []
    for slot in sorted(source_slots):
        for rel_path in source_slots[slot]:
            path = base / rel_path
            if not path.is_file():
                diagnostics.append(
                    Diagnostic(
                        code="pdx.missing_source",
                        message=f"PDX source {rel_path} does not exist.",
                        module_id=module_id,
                        collection_id=collection_id,
                        slot=slot,
                        source_path=rel_path,
                    )
                )
                continue
            try:
                block = PDXBlock.from_file(path)
                # Generated output follows the module's logical source name,
                # even when that source happens to be a symlink.
                block.file_ext = Path(rel_path).suffix or None
            except FileNotFoundError:
                diagnostics.append(
                    Diagnostic(
                        code="pdx.missing_source",
                        message=f"PDX source {rel_path} does not exist.",
                        module_id=module_id,
                        collection_id=collection_id,
                        slot=slot,
                        source_path=rel_path,
                    )
                )
                continue
            except OSError as error:
                diagnostics.append(
                    Diagnostic(
                        code="pdx.unreadable_source",
                        message=f"PDX source {rel_path} cannot be read. {_os_error_text(error)}.",
                        module_id=module_id,
                        collection_id=collection_id,
                        slot=slot,
                        source_path=rel_path,
                    )
                )
                continue
            except PDXParseError as error:
                diagnostics.extend(
                    _pdx_parse_diagnostics(
                        error.diagnostics,
                        rel_path=rel_path,
                        module_id=module_id,
                        collection_id=collection_id,
                        slot=slot,
                    )
                )
                continue
            sources.append(PDXBlockSource(slot=slot, path=rel_path, block=block))
    return PDXLoadResult(sources=tuple(sources), diagnostics=tuple(diagnostics))


def load_module_sources(
    root: str | Path,
    source_slots: Mapping[str, Sequence[str | Path]],
    *,
    module_id: str | None = None,
    inferred_type: str | None = None,
    slots: Sequence[Slot] = (),
    metadata_keys: Sequence[str] = (),
    strict_metadata: bool = False,
    pdx_slots: Sequence[str] = DEFAULT_PDX_SLOTS,
    loc_slots: Sequence[str] = DEFAULT_LOC_SLOTS,
    copy_slots: Sequence[str] = DEFAULT_COPY_SLOTS,
) -> ModuleSourceBundle:
    """Load all generic source records for one module root.

    Args:
        root: Module source root.
        source_slots: Matched slot names to relative source paths.
        module_id: Optional module id for diagnostics and records.
        inferred_type: Optional module type inferred from ancestry.
        slots: Optional slot declarations with explicit loader roles.
        metadata_keys: Additional family-owned top-level metadata keys.
        strict_metadata: Whether unknown module metadata keys should be
            blocking errors instead of loose-mode warnings.
        pdx_slots: Slot names to parse as PDX files.
        loc_slots: Slot names to parse as localization files.
        copy_slots: Slot names to load as static copy sources.

    Returns:
        A normalized source bundle for family compilers.
    """

    normalized_slots = _normalized_source_slots(source_slots)
    metadata = load_metadata(
        root,
        inferred_type=inferred_type,
        module_id=module_id,
        metadata_keys=metadata_keys,
        strict_metadata=strict_metadata,
    )
    pdx = load_pdx_sources(
        root,
        _slot_subset(normalized_slots, _loader_slot_names(pdx_slots, slots, "pdx")),
        module_id=module_id,
    )
    loc = load_loc_sources(
        root,
        _slot_subset(normalized_slots, _loader_slot_names(loc_slots, slots, "loc")),
        module_id=module_id,
    )
    copy = load_copy_sources(
        root,
        _slot_subset(normalized_slots, _loader_slot_names(copy_slots, slots, "copy")),
        module_id=module_id,
    )
    return ModuleSourceBundle(
        root=str(Path(root)),
        source_slots=normalized_slots,
        metadata=metadata.metadata,
        pdx_sources=pdx.sources,
        loc_entries=loc.entries,
        copy_sources=copy.sources,
        diagnostics=(*metadata.diagnostics, *pdx.diagnostics, *loc.diagnostics, *copy.diagnostics),
        module_id=module_id,
    )


def _metadata_unknown_key_severity(strict_metadata: bool) -> str:
    return "error" if strict_metadata else "warning"


def load_loc_sources(
    root: str | Path,
    source_slots: Mapping[str, Sequence[str | Path]],
    *,
    module_id: str | None = None,
    collection_id: str | None = None,
) -> LocalizationLoadResult:
    """Load legacy INI-style `.loc` sources.

    Args:
        root: Module source root.
        source_slots: Slot name to relative `.loc` paths.
        module_id: Optional module id for entries and diagnostics.
        collection_id: Optional collection id for diagnostics.

    Returns:
        Localization entries and diagnostics.
    """

    base = Path(root)
    entries: list[LocalizationEntry] = []
    diagnostics: list[Diagnostic] = []
    seen: dict[tuple[str, str], LocalizationEntry] = {}
    for slot, rel_path in _ordered_source_paths(source_slots):
        path = base / rel_path
        if not path.is_file():
            diagnostics.append(
                _loc_diagnostic(
                    rel_path,
                    module_id,
                    collection_id,
                    slot,
                    "loc.missing_source",
                    f"Localization source {rel_path} does not exist.",
                )
            )
            continue
        try:
            text = path.read_text(encoding="utf-8-sig")
        except OSError as error:
            diagnostics.append(
                _loc_diagnostic(
                    rel_path,
                    module_id,
                    collection_id,
                    slot,
                    "loc.unreadable_source",
                    f"Localization source {rel_path} cannot be read. {_os_error_text(error)}.",
                )
            )
            continue
        loaded = _parse_loc_text(text, rel_path=rel_path, module_id=module_id, collection_id=collection_id, slot=slot)
        diagnostics.extend(loaded.diagnostics)
        for entry in loaded.entries:
            previous = seen.get((entry.language, entry.key))
            if previous:
                diagnostics.append(
                    _loc_diagnostic(
                        rel_path,
                        module_id,
                        collection_id,
                        slot,
                        "loc.duplicate_key",
                        (f"Localization key {entry.key!r} for {entry.language!r} " f"is declared by {previous.source_path} and {entry.source_path}."),
                    )
                )
            else:
                seen[(entry.language, entry.key)] = entry
            entries.append(entry)
    return LocalizationLoadResult(entries=tuple(entries), diagnostics=tuple(diagnostics))


def _parse_loc_text(
    text: str,
    *,
    rel_path: str,
    module_id: str | None,
    collection_id: str | None,
    slot: str,
) -> LocalizationLoadResult:
    document = parse_source(text)
    entries = tuple(
        LocalizationEntry(
            key=entry.key,
            language=entry.language,
            text=entry.text,
            source_path=rel_path,
            module_id=module_id,
        )
        for entry in document.entries
    )
    diagnostics = tuple(
        (
            _loc_diagnostic(
                rel_path,
                module_id,
                collection_id,
                slot,
                "loc.missing_language",
                f"Localization line {issue.line} must appear after a language header.",
            )
            if issue.code == "missing_language"
            else _loc_invalid_line(
                rel_path,
                module_id,
                collection_id,
                slot,
                issue.line,
            )
        )
        for issue in document.issues
    )
    return LocalizationLoadResult(entries=entries, diagnostics=diagnostics)


def _loc_invalid_line(
    path: str,
    module_id: str | None,
    collection_id: str | None,
    slot: str,
    line_number: int,
) -> Diagnostic:
    return _loc_diagnostic(
        path,
        module_id,
        collection_id,
        slot,
        "loc.invalid_line",
        f"Localization line {line_number} must be '[language]' or 'key=value'.",
    )


def load_copy_sources(
    root: str | Path,
    source_slots: Mapping[str, Sequence[str | Path]],
    *,
    module_id: str | None = None,
    collection_id: str | None = None,
) -> CopyLoadResult:
    """Load static copy source metadata.

    Args:
        root: Module source root.
        source_slots: Slot name to relative source paths.
        module_id: Optional module id for diagnostics.
        collection_id: Optional collection id for diagnostics.

    Returns:
        Copy source records and diagnostics.
    """

    base = Path(root)
    sources: list[CopySource] = []
    diagnostics: list[Diagnostic] = []
    for slot, rel_path in _ordered_source_paths(source_slots):
        path = base / rel_path
        if not path.is_file():
            diagnostics.append(
                Diagnostic(
                    code="copy.missing_source",
                    message=f"Static copy source {rel_path} does not exist.",
                    module_id=module_id,
                    collection_id=collection_id,
                    slot=slot,
                    source_path=rel_path,
                )
            )
            continue
        try:
            payload = path.read_bytes()
        except OSError as error:
            diagnostics.append(
                Diagnostic(
                    code="copy.unreadable_source",
                    message=f"Static copy source {rel_path} cannot be read. {_os_error_text(error)}.",
                    module_id=module_id,
                    collection_id=collection_id,
                    slot=slot,
                    source_path=rel_path,
                )
            )
            continue
        metadata = _copy_image_metadata(path, payload)
        sources.append(
            CopySource(
                slot=slot,
                path=rel_path,
                output_path=rel_path,
                sha256=sha256hash(payload),
                size=len(payload),
                content_sha256=content_sha256(payload),
                media_type=metadata.get("media_type"),
                format=metadata.get("format"),
                width=metadata.get("width"),
                height=metadata.get("height"),
            )
        )
    return CopyLoadResult(sources=tuple(sources), diagnostics=tuple(diagnostics))


def _copy_image_metadata(path: Path, payload: bytes) -> dict[str, str | int]:
    suffix = path.suffix.lower()
    if suffix == ".png":
        return _png_metadata(payload)
    if suffix == ".dds":
        return _dds_metadata(payload)
    if suffix == ".tga":
        return _tga_metadata(payload)
    return {}


def _png_metadata(payload: bytes) -> dict[str, str | int]:
    if len(payload) < 24 or not payload.startswith(b"\x89PNG\r\n\x1a\n") or payload[12:16] != b"IHDR":
        return {}
    width = unpack_from(">I", payload, 16)[0]
    height = unpack_from(">I", payload, 20)[0]
    return _image_metadata("image/png", "png", width, height)


def _dds_metadata(payload: bytes) -> dict[str, str | int]:
    if len(payload) < 20 or not payload.startswith(b"DDS "):
        return {}
    height = unpack_from("<I", payload, 12)[0]
    width = unpack_from("<I", payload, 16)[0]
    return _image_metadata("image/vnd-ms-dds", "dds", width, height)


def _tga_metadata(payload: bytes) -> dict[str, str | int]:
    if len(payload) < 18:
        return {}
    width = unpack_from("<H", payload, 12)[0]
    height = unpack_from("<H", payload, 14)[0]
    return _image_metadata("image/x-tga", "tga", width, height)


def _image_metadata(media_type: str, file_format: str, width: int, height: int) -> dict[str, str | int]:
    if width <= 0 or height <= 0:
        return {}
    return {
        "media_type": media_type,
        "format": file_format,
        "width": width,
        "height": height,
    }


def _os_error_text(error: OSError) -> str:
    return error.strerror or str(error) or error.__class__.__name__


def _module_metadata_read_diagnostics(
    read: _MetadataReadResult,
    *,
    module_id: str | None,
    source_path: str,
) -> tuple[Diagnostic, ...]:
    if read.invalid_yaml:
        return (
            Diagnostic(
                code="metadata.invalid_yaml",
                message=("meta.yaml contains invalid YAML." if source_path == "meta.yaml" else f"{source_path} contains invalid YAML."),
                module_id=module_id,
                source_path=source_path,
            ),
        )
    if read.unreadable_error:
        return (
            Diagnostic(
                code="metadata.unreadable_source",
                message=(
                    "meta.yaml cannot be read. " f"{read.unreadable_error}."
                    if source_path == "meta.yaml"
                    else (f"{source_path} cannot be read. " f"{read.unreadable_error}.")
                ),
                module_id=module_id,
                source_path=source_path,
            ),
        )
    if read.invalid_mapping:
        return (
            Diagnostic(
                code="metadata.invalid_yaml",
                message=("meta.yaml must contain a YAML mapping." if source_path == "meta.yaml" else f"{source_path} must contain a YAML mapping."),
                module_id=module_id,
                source_path=source_path,
            ),
        )
    return ()


def _collection_metadata_read_diagnostics(
    read: _MetadataReadResult,
    *,
    collection_id: str,
    source_path: str,
) -> tuple[Diagnostic, ...]:
    if read.invalid_yaml:
        return (
            Diagnostic(
                code="collection_metadata.invalid_yaml",
                message=(
                    "Collection metadata contains invalid YAML." if source_path in {"meta.yaml", "collection.yaml"} else f"{source_path} contains invalid YAML."
                ),
                collection_id=collection_id,
                source_path=source_path,
            ),
        )
    if read.unreadable_error:
        return (
            Diagnostic(
                code="collection_metadata.unreadable_source",
                message=(
                    "Collection metadata cannot be read. " f"{read.unreadable_error}."
                    if source_path in {"meta.yaml", "collection.yaml"}
                    else (f"{source_path} cannot be read. " f"{read.unreadable_error}.")
                ),
                collection_id=collection_id,
                source_path=source_path,
            ),
        )
    if read.invalid_mapping:
        return (
            Diagnostic(
                code="collection_metadata.invalid_yaml",
                message=(
                    "Collection metadata must contain a YAML mapping."
                    if source_path in {"meta.yaml", "collection.yaml"}
                    else f"{source_path} must contain a YAML mapping."
                ),
                collection_id=collection_id,
                source_path=source_path,
            ),
        )
    return ()


def _read_metadata(path: Path) -> _MetadataReadResult:
    if not path.exists():
        return _MetadataReadResult(data={})
    try:
        value = load_yaml_text(
            load_txt(str(path), encoding="utf-8", strict=True),
            Loader=_MetadataYamlLoader,
        )
    except OSError as error:
        return _MetadataReadResult(data={}, unreadable_error=_os_error_text(error))
    except YAMLError:
        return _MetadataReadResult(data={}, invalid_yaml=True)
    if not isinstance(value, dict):
        return _MetadataReadResult(data={}, invalid_mapping=True)
    return _MetadataReadResult(data=value)


def _collection_metadata_path(root: Path) -> Path:
    meta = root / "meta.yaml"
    return meta if meta.exists() else root / "collection.yaml"


def _folder_identity(name: str) -> tuple[str, str | None]:
    parts = name.split(" - ", 1)
    object_id = parts[0].strip()
    note = parts[1].strip() if len(parts) == 2 and parts[1].strip() else None
    return object_id, note


def _loc_diagnostic(
    path: str,
    module_id: str | None,
    collection_id: str | None,
    slot: str,
    code: str,
    message: str,
) -> Diagnostic:
    return Diagnostic(
        code=code,
        message=message,
        module_id=module_id,
        collection_id=collection_id,
        slot=slot,
        source_path=path,
    )


def _pdx_parse_diagnostics(
    rows: Sequence[PDXDiagnostic],
    *,
    rel_path: str,
    module_id: str | None,
    collection_id: str | None,
    slot: str,
) -> tuple[Diagnostic, ...]:
    return tuple(
        Diagnostic(
            code=row.code,
            message=row.message,
            module_id=module_id,
            collection_id=collection_id,
            slot=slot,
            source_path=rel_path,
            span={"line": row.line, "column": row.column},
        )
        for row in rows
    ) or (
        Diagnostic(
            code="pdx.parse_failed",
            message=f"PDX source {rel_path} failed to parse.",
            module_id=module_id,
            collection_id=collection_id,
            slot=slot,
            source_path=rel_path,
        ),
    )


def _ordered_source_paths(source_slots: Mapping[str, Sequence[str | Path]]) -> tuple[tuple[str, str], ...]:
    pairs = [(slot, str(path).replace("\\", "/")) for slot in sorted(source_slots) for path in source_slots[slot]]
    return tuple(sorted(pairs, key=lambda pair: (pair[1], pair[0])))


def _normalized_source_slots(source_slots: Mapping[str, Sequence[str | Path]]) -> dict[str, tuple[str, ...]]:
    return {slot: tuple(str(path).replace("\\", "/") for path in source_slots[slot]) for slot in sorted(source_slots)}


def _default_collection_source_slots(root: Path) -> dict[str, tuple[str, ...]]:
    source_slots: dict[str, tuple[str, ...]] = {}
    if (root / "def.txt").is_file():
        source_slots["def"] = ("def.txt",)
    loc_paths = tuple(path.relative_to(root).as_posix() for path in sorted(root.rglob("*.loc")) if path.is_file())
    if loc_paths:
        source_slots["loc"] = loc_paths
    return source_slots


def _slot_subset(source_slots: Mapping[str, tuple[str, ...]], names: Sequence[str]) -> dict[str, tuple[str, ...]]:
    wanted = set(names)
    return {slot: source_slots[slot] for slot in sorted(source_slots) if slot in wanted}


def _loader_slot_names(defaults: Sequence[str], slots: Sequence[Slot], kind: str) -> tuple[str, ...]:
    names = [*defaults]
    names.extend(slot.name for slot in slots if slot.kind == kind)
    return tuple(dict.fromkeys(names))


def _metadata_text(metadata: Mapping[str, Any], key: str) -> str | None:
    value = metadata.get(key)
    return value if isinstance(value, str) and value else None
