"""Durable recovery contract for compound diagram module creation."""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import TYPE_CHECKING, cast

from heavenbase.utils import dumps_json, loads_json, pj

if TYPE_CHECKING:
    from paradev.build._fs import AnchoredDirectory

DIAGRAM_MODULE_RECOVERY_SCHEMA = "paradev.diagram-module-recovery.v1"
DIAGRAM_MODULE_RECOVERY_DIRECTORY = ".paradev/diagram-module-transaction"
DIAGRAM_MODULE_RECOVERY_JOURNAL = "recovery.json"
MAX_DIAGRAM_MODULE_RECOVERY_BYTES = 1024 * 1024
MAX_DIAGRAM_MODULE_RECOVERY_FILES = 256
MAX_DIAGRAM_MODULE_RECOVERY_SOURCES = 256

_DIGEST = re.compile(r"\A[0-9a-f]{64}\Z")
_TRANSACTION_ID = re.compile(r"\A[0-9a-f]{32}\Z")
_JOURNAL_FIELDS = frozenset(
    {
        "schema",
        "transaction_id",
        "project_root_identity",
        "source_root",
        "family",
        "object_id",
        "folder_name",
        "files",
        "sources",
    }
)
_FILE_FIELDS = frozenset({"path", "size", "sha256"})
_SOURCE_FIELDS = frozenset(
    {
        "path",
        "before_size",
        "before_sha256",
        "after_size",
        "after_sha256",
    }
)


@dataclass(frozen=True, slots=True)
class DiagramModuleRecoveryFile:
    """One exact file expected inside the new standalone module."""

    path: str
    size: int
    sha256: str

    def to_dict(self) -> dict[str, object]:
        """Return the canonical JSON-safe file row."""

        return {
            "path": self.path,
            "size": self.size,
            "sha256": self.sha256,
        }


@dataclass(frozen=True, slots=True)
class DiagramModuleRecoverySource:
    """One existing source file's exact before and after states."""

    path: str
    before_size: int
    before_sha256: str
    after_size: int
    after_sha256: str

    def to_dict(self) -> dict[str, object]:
        """Return the canonical JSON-safe source row."""

        return {
            "path": self.path,
            "before_size": self.before_size,
            "before_sha256": self.before_sha256,
            "after_size": self.after_size,
            "after_sha256": self.after_sha256,
        }


@dataclass(frozen=True, slots=True)
class DiagramModuleRecoveryJournal:
    """One bounded compound module-create recovery record."""

    transaction_id: str
    project_root_identity: tuple[int, int]
    source_root: str
    family: str
    object_id: str
    folder_name: str
    files: tuple[DiagramModuleRecoveryFile, ...]
    sources: tuple[DiagramModuleRecoverySource, ...]

    @property
    def module_path(self) -> str:
        """Return the project-relative canonical module directory."""

        prefix = "" if self.source_root == "." else f"{self.source_root}/"
        return f"{prefix}modules/{self.family}/{self.folder_name}"

    @property
    def scaffold_transaction_path(self) -> str:
        """Return the project-relative hidden scaffold transaction path."""

        prefix = "" if self.source_root == "." else f"{self.source_root}/"
        return f"{prefix}.paradev/module-transactions/batch-{self.transaction_id}.txn"

    def to_dict(self) -> dict[str, object]:
        """Return the canonical JSON-safe journal."""

        return {
            "schema": DIAGRAM_MODULE_RECOVERY_SCHEMA,
            "transaction_id": self.transaction_id,
            "project_root_identity": list(self.project_root_identity),
            "source_root": self.source_root,
            "family": self.family,
            "object_id": self.object_id,
            "folder_name": self.folder_name,
            "files": [item.to_dict() for item in self.files],
            "sources": [item.to_dict() for item in self.sources],
        }


def diagram_module_recovery_root(project_root: str) -> str:
    """Return the fixed hidden recovery directory for one project."""

    return pj(project_root, DIAGRAM_MODULE_RECOVERY_DIRECTORY)


def write_diagram_module_recovery(
    authority: AnchoredDirectory,
    journal: DiagramModuleRecoveryJournal,
) -> None:
    """Atomically persist and fsync one canonical recovery journal."""

    payload = (
        dumps_json(
            journal.to_dict(),
            compact=True,
            sort_keys=True,
        )
        + "\n"
    ).encode()
    if len(payload) > MAX_DIAGRAM_MODULE_RECOVERY_BYTES:
        raise ValueError("Diagram module recovery journal exceeds its bounded size.")
    authority.write_bytes(
        DIAGRAM_MODULE_RECOVERY_JOURNAL,
        payload,
        mode=0o600,
    )


def read_diagram_module_recovery(
    authority: AnchoredDirectory,
) -> DiagramModuleRecoveryJournal | None:
    """Read and strictly validate one private recovery journal."""

    payload = authority.read_bytes(DIAGRAM_MODULE_RECOVERY_JOURNAL)
    if payload is None:
        return None
    if len(payload) > MAX_DIAGRAM_MODULE_RECOVERY_BYTES:
        raise ValueError("Diagram module recovery journal exceeds its bounded size.")
    try:
        raw = loads_json(payload.decode())
    except (UnicodeDecodeError, ValueError) as error:
        raise ValueError("Diagram module recovery journal is not valid UTF-8 JSON.") from error
    if not isinstance(raw, Mapping):
        raise ValueError("Diagram module recovery journal must be a JSON object.")
    return _journal_from_mapping(cast(Mapping[object, object], raw))


def _journal_from_mapping(
    raw: Mapping[object, object],
) -> DiagramModuleRecoveryJournal:
    _require_fields(raw, _JOURNAL_FIELDS, label="journal")
    if raw.get("schema") != DIAGRAM_MODULE_RECOVERY_SCHEMA:
        raise ValueError(f"Unsupported diagram module recovery schema: {raw.get('schema')!r}.")
    transaction_id = _required_string(
        raw.get("transaction_id"),
        label="transaction_id",
    )
    if _TRANSACTION_ID.fullmatch(transaction_id) is None:
        raise ValueError("Diagram module recovery transaction_id is invalid.")
    identity = _identity(
        raw.get("project_root_identity"),
        label="project_root_identity",
    )
    source_root = _relative_path(raw.get("source_root"), label="source_root")
    family = _component(raw.get("family"), label="family")
    object_id = _component(raw.get("object_id"), label="object_id")
    folder_name = _component(raw.get("folder_name"), label="folder_name")
    raw_files = _mapping_rows(
        raw.get("files"),
        label="files",
        maximum=MAX_DIAGRAM_MODULE_RECOVERY_FILES,
    )
    raw_sources = _mapping_rows(
        raw.get("sources"),
        label="sources",
        maximum=MAX_DIAGRAM_MODULE_RECOVERY_SOURCES,
    )
    files = tuple(_file_from_mapping(item) for item in raw_files)
    sources = tuple(_source_from_mapping(item) for item in raw_sources)
    if not files:
        raise ValueError("Diagram module recovery must own at least one module file.")
    if not sources:
        raise ValueError("Diagram module recovery must guard at least one source file.")
    _require_unique((item.path for item in files), label="module file paths")
    _require_unique((item.path for item in sources), label="source paths")
    return DiagramModuleRecoveryJournal(
        transaction_id=transaction_id,
        project_root_identity=identity,
        source_root=source_root,
        family=family,
        object_id=object_id,
        folder_name=folder_name,
        files=files,
        sources=sources,
    )


def _file_from_mapping(
    raw: Mapping[object, object],
) -> DiagramModuleRecoveryFile:
    _require_fields(raw, _FILE_FIELDS, label="file row")
    path = _relative_path(raw.get("path"), label="file path")
    if path == ".":
        raise ValueError("Diagram module recovery file path must name a file.")
    return DiagramModuleRecoveryFile(
        path=path,
        size=_nonnegative_int(raw.get("size"), label="file size"),
        sha256=_digest(raw.get("sha256"), label="file sha256"),
    )


def _source_from_mapping(
    raw: Mapping[object, object],
) -> DiagramModuleRecoverySource:
    _require_fields(raw, _SOURCE_FIELDS, label="source row")
    path = _relative_path(raw.get("path"), label="source path")
    if path == ".":
        raise ValueError("Diagram module recovery source path must name a file.")
    return DiagramModuleRecoverySource(
        path=path,
        before_size=_nonnegative_int(
            raw.get("before_size"),
            label="source before_size",
        ),
        before_sha256=_digest(
            raw.get("before_sha256"),
            label="source before_sha256",
        ),
        after_size=_nonnegative_int(
            raw.get("after_size"),
            label="source after_size",
        ),
        after_sha256=_digest(
            raw.get("after_sha256"),
            label="source after_sha256",
        ),
    )


def _mapping_rows(
    value: object,
    *,
    label: str,
    maximum: int,
) -> tuple[Mapping[object, object], ...]:
    if not isinstance(value, list):
        raise ValueError(f"Diagram module recovery {label} must be a list.")
    if len(value) > maximum:
        raise ValueError(f"Diagram module recovery {label} exceed the bounded count.")
    if any(not isinstance(item, Mapping) for item in value):
        raise ValueError(f"Diagram module recovery {label} rows must be JSON objects.")
    return tuple(cast(Mapping[object, object], item) for item in value)


def _require_fields(
    raw: Mapping[object, object],
    expected: frozenset[str],
    *,
    label: str,
) -> None:
    fields = set(raw)
    if fields != expected:
        missing = sorted(expected - fields)
        unknown = sorted(str(field) for field in fields - expected)
        detail = []
        if missing:
            detail.append(f"missing {', '.join(missing)}")
        if unknown:
            detail.append(f"unknown {', '.join(unknown)}")
        raise ValueError(f"Diagram module recovery {label} fields are invalid: {'; '.join(detail)}.")


def _required_string(value: object, *, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"Diagram module recovery {label} must be non-empty text.")
    return value


def _relative_path(value: object, *, label: str) -> str:
    text = _required_string(value, label=label)
    if text == ".":
        return text
    path = PurePosixPath(text)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError(f"Diagram module recovery {label} must be a normalized relative path.")
    return path.as_posix()


def _component(value: object, *, label: str) -> str:
    text = _required_string(value, label=label)
    if text in {".", ".."} or "/" in text or "\\" in text:
        raise ValueError(f"Diagram module recovery {label} must be one path component.")
    return text


def _identity(value: object, *, label: str) -> tuple[int, int]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or len(value) != 2 or any(type(item) is not int or item < 0 for item in value):
        raise ValueError(f"Diagram module recovery {label} must contain two nonnegative integers.")
    return cast(tuple[int, int], tuple(value))


def _nonnegative_int(value: object, *, label: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"Diagram module recovery {label} must be a nonnegative integer.")
    return value


def _digest(value: object, *, label: str) -> str:
    if not isinstance(value, str) or _DIGEST.fullmatch(value) is None:
        raise ValueError(f"Diagram module recovery {label} must be a lowercase SHA-256 digest.")
    return value


def _require_unique(values: Iterable[str], *, label: str) -> None:
    rows = tuple(values)
    if len(rows) != len(set(rows)):
        raise ValueError(f"Diagram module recovery {label} must be unique.")
