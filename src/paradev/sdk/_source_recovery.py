"""Durable private journal contract for source-authoring transactions."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Literal, cast

from heavenbase.utils import dumps_json, loads_json, pj

if TYPE_CHECKING:
    from paradev.build._fs import AnchoredDirectory

SOURCE_DRAFT_RECOVERY_SCHEMA = "paradev.source-draft-recovery.v5"
_V4_SOURCE_DRAFT_RECOVERY_SCHEMA = "paradev.source-draft-recovery.v4"
_LEGACY_SOURCE_DRAFT_RECOVERY_SCHEMA = "paradev.source-draft-recovery.v3"
SOURCE_DRAFT_RECOVERY_DIRECTORY = ".paradev/source-draft-transaction"
SOURCE_DRAFT_RECOVERY_JOURNAL = "recovery.json"
MAX_SOURCE_DRAFT_RECOVERY_JOURNAL_BYTES = 1024 * 1024
MAX_SOURCE_DRAFT_RECOVERY_FILES = 256

RecoveryPhase = Literal[
    "preparing",
    "applying",
    "recovery_required",
    "committed",
]
RecoveryStep = Literal["pending", "applying", "applied"]

_DIGEST = re.compile(r"\A[0-9a-f]{64}\Z")
_TRANSACTION_ID = re.compile(r"\A[0-9a-f]{32}\Z")
_JOURNAL_FIELDS = frozenset(
    {
        "schema",
        "transaction_id",
        "project_root_identity",
        "phase",
        "files",
        "rename",
    }
)
_FILE_FIELDS = frozenset(
    {
        "path",
        "backup",
        "displaced",
        "mode",
        "size",
        "before_sha256",
        "after_exists",
        "after_size",
        "after_sha256",
        "state",
    }
)
_RENAME_FIELDS = frozenset(
    {
        "operation",
        "container",
        "source_root",
        "family",
        "previous_name",
        "target_name",
        "previous_object_id",
        "target_object_id",
        "directory_identity",
        "state",
    }
)
_V4_RENAME_FIELDS = _RENAME_FIELDS - {"operation"}
_LEGACY_RENAME_FIELDS = _V4_RENAME_FIELDS - {"container"}


@dataclass(frozen=True, slots=True)
class SourceDraftRecoveryFile:
    """One source file's before/after ownership evidence."""

    path: str
    backup: str | None
    displaced: str | None
    mode: int | None
    size: int
    before_sha256: str | None
    after_exists: bool
    after_size: int
    after_sha256: str | None
    state: RecoveryStep = "pending"

    def to_dict(self) -> dict[str, object]:
        """Return the canonical JSON-safe file row."""

        return {
            "path": self.path,
            "backup": self.backup,
            "displaced": self.displaced,
            "mode": self.mode,
            "size": self.size,
            "before_sha256": self.before_sha256,
            "after_exists": self.after_exists,
            "after_size": self.after_size,
            "after_sha256": self.after_sha256,
            "state": self.state,
        }


@dataclass(frozen=True, slots=True)
class SourceDraftRecoveryRename:
    """One optional Registry-container folder commit step."""

    source_root: str
    family: str
    previous_name: str
    target_name: str
    previous_object_id: str
    target_object_id: str
    directory_identity: tuple[int, int]
    operation: Literal["rename", "remove"] = "rename"
    container: Literal["modules", "collections"] = "modules"
    state: RecoveryStep = "pending"

    def to_dict(self) -> dict[str, object]:
        """Return the canonical JSON-safe rename row."""

        return {
            "operation": self.operation,
            "container": self.container,
            "source_root": self.source_root,
            "family": self.family,
            "previous_name": self.previous_name,
            "target_name": self.target_name,
            "previous_object_id": self.previous_object_id,
            "target_object_id": self.target_object_id,
            "directory_identity": list(self.directory_identity),
            "state": self.state,
        }


@dataclass(frozen=True, slots=True)
class SourceDraftRecoveryJournal:
    """Complete bounded source transaction recovery state."""

    transaction_id: str
    project_root_identity: tuple[int, int]
    phase: RecoveryPhase
    files: tuple[SourceDraftRecoveryFile, ...]
    rename: SourceDraftRecoveryRename | None = None

    def to_dict(self) -> dict[str, object]:
        """Return the canonical JSON-safe journal."""

        return {
            "schema": SOURCE_DRAFT_RECOVERY_SCHEMA,
            "transaction_id": self.transaction_id,
            "project_root_identity": list(self.project_root_identity),
            "phase": self.phase,
            "files": [item.to_dict() for item in self.files],
            "rename": self.rename.to_dict() if self.rename is not None else None,
        }

    def with_file_state(
        self,
        index: int,
        state: RecoveryStep,
    ) -> SourceDraftRecoveryJournal:
        """Return a journal with one file step advanced."""

        files = list(self.files)
        files[index] = replace(files[index], state=state)
        return replace(self, files=tuple(files))

    def with_rename_state(
        self,
        state: RecoveryStep,
    ) -> SourceDraftRecoveryJournal:
        """Return a journal with its rename step advanced."""

        if self.rename is None:
            raise ValueError("Source recovery journal has no folder rename step.")
        return replace(self, rename=replace(self.rename, state=state))


def source_draft_recovery_root(project_root: str) -> str:
    """Return the fixed hidden transaction directory for one mutation root."""

    return pj(project_root, SOURCE_DRAFT_RECOVERY_DIRECTORY)


def source_draft_recovery_displaced_path(
    source_path: str,
    transaction_id: str,
    index: int,
) -> str:
    """Return one deterministic same-directory displacement path."""

    parent, separator, _name = source_path.rpartition("/")
    displaced_name = f".paradev-draft-{transaction_id}-{index:04d}.displaced"
    return f"{parent}/{displaced_name}" if separator else displaced_name


def write_source_draft_recovery(
    authority: AnchoredDirectory,
    journal: SourceDraftRecoveryJournal,
) -> None:
    """Atomically persist and fsync one canonical journal."""

    payload = (
        dumps_json(
            journal.to_dict(),
            compact=True,
            sort_keys=True,
        )
        + "\n"
    ).encode()
    if len(payload) > MAX_SOURCE_DRAFT_RECOVERY_JOURNAL_BYTES:
        raise ValueError("Source draft recovery journal exceeds its bounded size.")
    authority.write_bytes(
        SOURCE_DRAFT_RECOVERY_JOURNAL,
        payload,
        mode=0o600,
    )


def read_source_draft_recovery(
    authority: AnchoredDirectory,
) -> SourceDraftRecoveryJournal | None:
    """Read and strictly validate one private journal."""

    payload = authority.read_bytes(SOURCE_DRAFT_RECOVERY_JOURNAL)
    if payload is None:
        return None
    if len(payload) > MAX_SOURCE_DRAFT_RECOVERY_JOURNAL_BYTES:
        raise ValueError("Source draft recovery journal exceeds its bounded size.")
    try:
        raw = loads_json(payload.decode())
    except (UnicodeDecodeError, ValueError) as error:
        raise ValueError("Source draft recovery journal is not valid UTF-8 JSON.") from error
    if not isinstance(raw, Mapping):
        raise ValueError("Source draft recovery journal must be a JSON object.")
    return _journal_from_mapping(cast(Mapping[object, object], raw))


def _journal_from_mapping(
    raw: Mapping[object, object],
) -> SourceDraftRecoveryJournal:
    _require_fields(raw, _JOURNAL_FIELDS, label="journal")
    schema = raw.get("schema")
    if schema not in {
        SOURCE_DRAFT_RECOVERY_SCHEMA,
        _V4_SOURCE_DRAFT_RECOVERY_SCHEMA,
        _LEGACY_SOURCE_DRAFT_RECOVERY_SCHEMA,
    }:
        raise ValueError(f"Unsupported source draft recovery schema: {raw.get('schema')!r}.")
    transaction_id = _required_string(
        raw.get("transaction_id"),
        label="transaction_id",
    )
    if _TRANSACTION_ID.fullmatch(transaction_id) is None:
        raise ValueError("Source draft recovery transaction_id is invalid.")
    project_root_identity = _identity(
        raw.get("project_root_identity"),
        label="project_root_identity",
    )
    phase = raw.get("phase")
    if phase not in {
        "preparing",
        "applying",
        "recovery_required",
        "committed",
    }:
        raise ValueError("Source draft recovery phase is invalid.")
    raw_files = raw.get("files")
    if not isinstance(raw_files, list):
        raise ValueError("Source draft recovery files must be a list.")
    if len(raw_files) > MAX_SOURCE_DRAFT_RECOVERY_FILES:
        raise ValueError("Source draft recovery files exceed the bounded count.")
    files = tuple(_file_from_mapping(item) for item in raw_files)
    paths = [item.path for item in files]
    if len(paths) != len(set(paths)):
        raise ValueError("Source draft recovery file paths must be unique.")
    for index, item in enumerate(files):
        if item.displaced is not None and item.displaced != (
            source_draft_recovery_displaced_path(
                item.path,
                transaction_id,
                index,
            )
        ):
            raise ValueError("Source draft recovery displaced path does not match its " "transaction-owned location.")
    raw_rename = raw.get("rename")
    rename = (
        None
        if raw_rename is None
        else _rename_from_mapping(
            raw_rename,
            schema=cast(str, schema),
        )
    )
    return SourceDraftRecoveryJournal(
        transaction_id=transaction_id,
        project_root_identity=project_root_identity,
        phase=cast(RecoveryPhase, phase),
        files=files,
        rename=rename,
    )


def _file_from_mapping(raw: object) -> SourceDraftRecoveryFile:
    if not isinstance(raw, Mapping):
        raise ValueError("Source draft recovery file row must be an object.")
    row = cast(Mapping[object, object], raw)
    _require_fields(row, _FILE_FIELDS, label="file row")
    path = _relative_path(row.get("path"), label="file path")
    backup_raw = row.get("backup")
    backup = None if backup_raw is None else _relative_path(backup_raw, label="backup path")
    displaced_raw = row.get("displaced")
    displaced = None if displaced_raw is None else _relative_path(displaced_raw, label="displaced path")
    mode = _optional_nonnegative_int(row.get("mode"), label="mode")
    size = _nonnegative_int(row.get("size"), label="size")
    before_sha256 = _optional_digest(
        row.get("before_sha256"),
        label="before_sha256",
    )
    after_exists = row.get("after_exists")
    if not isinstance(after_exists, bool):
        raise ValueError("Source draft recovery after_exists must be boolean.")
    after_size = _nonnegative_int(row.get("after_size"), label="after_size")
    after_sha256 = _optional_digest(
        row.get("after_sha256"),
        label="after_sha256",
    )
    state = _step(row.get("state"))
    if backup is None:
        if mode is not None or size != 0 or before_sha256 is not None:
            raise ValueError("Absent source recovery rows cannot declare backup data.")
    elif before_sha256 is None:
        raise ValueError("Source recovery backup rows require before_sha256.")
    if after_exists:
        if after_sha256 is None:
            raise ValueError("Written source recovery rows require after_sha256.")
    elif after_size != 0 or after_sha256 is not None:
        raise ValueError("Removed source recovery rows cannot declare after data.")
    return SourceDraftRecoveryFile(
        path=path,
        backup=backup,
        displaced=displaced,
        mode=mode,
        size=size,
        before_sha256=before_sha256,
        after_exists=after_exists,
        after_size=after_size,
        after_sha256=after_sha256,
        state=state,
    )


def _rename_from_mapping(
    raw: object,
    *,
    schema: str,
) -> SourceDraftRecoveryRename:
    if not isinstance(raw, Mapping):
        raise ValueError("Source draft recovery rename must be an object.")
    row = cast(Mapping[object, object], raw)
    _require_fields(
        row,
        (
            _LEGACY_RENAME_FIELDS
            if schema == _LEGACY_SOURCE_DRAFT_RECOVERY_SCHEMA
            else _V4_RENAME_FIELDS if schema == _V4_SOURCE_DRAFT_RECOVERY_SCHEMA else _RENAME_FIELDS
        ),
        label="rename row",
    )
    legacy = schema == _LEGACY_SOURCE_DRAFT_RECOVERY_SCHEMA
    container = "modules" if legacy else row.get("container")
    if container not in {"modules", "collections"}:
        raise ValueError("Source draft recovery rename container must be 'modules' or " "'collections'.")
    operation = "rename" if schema != SOURCE_DRAFT_RECOVERY_SCHEMA else row.get("operation")
    if operation not in {"rename", "remove"}:
        raise ValueError("Source draft recovery operation must be 'rename' or 'remove'.")
    if operation == "remove" and container != "collections":
        raise ValueError("Source draft recovery removal must target the collections container.")
    source_root = _relative_path(
        row.get("source_root"),
        label="rename source_root",
        allow_root=True,
    )
    values = {
        field: _exact_component(row.get(field), label=f"rename {field}")
        for field in (
            "family",
            "previous_name",
            "target_name",
            "previous_object_id",
            "target_object_id",
        )
    }
    if values["previous_name"] == values["target_name"]:
        raise ValueError("Source draft recovery rename names must differ.")
    return SourceDraftRecoveryRename(
        source_root=source_root,
        family=values["family"],
        previous_name=values["previous_name"],
        target_name=values["target_name"],
        previous_object_id=values["previous_object_id"],
        target_object_id=values["target_object_id"],
        directory_identity=_identity(
            row.get("directory_identity"),
            label="rename directory_identity",
        ),
        operation=cast(Literal["rename", "remove"], operation),
        container=cast(Literal["modules", "collections"], container),
        state=_step(row.get("state")),
    )


def _require_fields(
    raw: Mapping[object, object],
    expected: frozenset[str],
    *,
    label: str,
) -> None:
    if any(not isinstance(key, str) for key in raw):
        raise ValueError(f"Source draft recovery {label} keys must be strings.")
    fields = frozenset(cast(str, key) for key in raw)
    if fields != expected:
        missing = ", ".join(sorted(expected - fields)) or "none"
        unknown = ", ".join(sorted(fields - expected)) or "none"
        raise ValueError(f"Source draft recovery {label} fields are invalid " f"(missing: {missing}; unknown: {unknown}).")


def _required_string(raw: object, *, label: str) -> str:
    if not isinstance(raw, str) or not raw:
        raise ValueError(f"Source draft recovery {label} must be a non-empty string.")
    return raw


def _relative_path(
    raw: object,
    *,
    label: str,
    allow_root: bool = False,
) -> str:
    value = _required_string(raw, label=label)
    if allow_root and value == ".":
        return value
    parts = value.split("/")
    if "\\" in value or value.startswith("/") or value == "." or any(part in {"", ".", ".."} for part in parts):
        raise ValueError(f"Source draft recovery {label} must be a normalized relative path.")
    return value


def _exact_component(raw: object, *, label: str) -> str:
    value = _required_string(raw, label=label)
    if value in {".", ".."} or "/" in value or "\\" in value:
        raise ValueError(f"Source draft recovery {label} must be one exact path component.")
    return value


def _identity(raw: object, *, label: str) -> tuple[int, int]:
    if not isinstance(raw, list) or len(raw) != 2 or any(not isinstance(item, int) or isinstance(item, bool) or item < 0 for item in raw):
        raise ValueError(f"Source draft recovery {label} must contain two non-negative integers.")
    return cast(tuple[int, int], tuple(raw))


def _nonnegative_int(raw: object, *, label: str) -> int:
    if not isinstance(raw, int) or isinstance(raw, bool) or raw < 0:
        raise ValueError(f"Source draft recovery {label} must be a non-negative integer.")
    return raw


def _optional_nonnegative_int(raw: object, *, label: str) -> int | None:
    if raw is None:
        return None
    return _nonnegative_int(raw, label=label)


def _optional_digest(raw: object, *, label: str) -> str | None:
    if raw is None:
        return None
    if not isinstance(raw, str) or _DIGEST.fullmatch(raw) is None:
        raise ValueError(f"Source draft recovery {label} must be a lowercase SHA-256 digest.")
    return raw


def _step(raw: object) -> RecoveryStep:
    if raw not in {"pending", "applying", "applied"}:
        raise ValueError("Source draft recovery step state is invalid.")
    return cast(RecoveryStep, raw)
