"""Pure planning for redundant inferred module-metadata cleanup."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Literal

from heavenbase.utils import loads_yaml, sha256hash

MODULE_METADATA_CLEANUP_POLICY = "paradev.module-metadata-cleanup-policy.v1"
MetadataCleanupAction = Literal["unchanged", "update", "remove", "blocked"]

_SIMPLE_TYPE_LINE = re.compile(rb"type:[ \t]+([A-Za-z0-9_.+\-]+)[ \t]*(?:\r\n|\n|\r)?\Z")
_YAML_WHITESPACE = b" \t\r\n"


@dataclass(frozen=True, slots=True)
class MetadataCleanupDiagnostic:
    """One fail-closed metadata-cleanup diagnostic."""

    code: str
    message: str
    source_path: str
    severity: str = "error"

    def to_view(self) -> dict[str, str]:
        """Return a JSON-safe diagnostic row."""

        return {
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
            "source_path": self.source_path,
        }


@dataclass(frozen=True, slots=True)
class MetadataCleanupDraft:
    """One immutable cleanup decision for already-snapshotted metadata bytes.

    `replacement` contains bytes only for an `update` action. A `remove`
    action deliberately has no target bytes, while `unchanged` and `blocked`
    actions never ask an orchestrator to mutate the source. `current_sha256`
    is absent only when invalid UTF-8 prevents an exact HeavenBase text hash;
    such a draft is always blocked.
    """

    source_path: str
    inferred_type: str
    action: MetadataCleanupAction
    current_size: int
    current_sha256: str | None
    target_exists: bool | None
    target_size: int | None
    target_sha256: str | None
    replacement: bytes | None = field(repr=False)
    removed_keys: tuple[str, ...] = ()
    diagnostics: tuple[MetadataCleanupDiagnostic, ...] = ()

    @property
    def blocked(self) -> bool:
        """Return whether source ambiguity prevents cleanup."""

        return self.action == "blocked"

    @property
    def changed(self) -> bool:
        """Return whether applying this draft would mutate the source."""

        return self.action in {"update", "remove"}

    def to_view(self) -> dict[str, object]:
        """Return the content-free portion of this cleanup decision."""

        planned: dict[str, object] | None = None
        if self.target_exists is not None:
            planned = {"exists": self.target_exists}
            if self.target_exists:
                planned.update(
                    {
                        "size_bytes": self.target_size,
                        "sha256": self.target_sha256,
                    }
                )
        return {
            "policy": MODULE_METADATA_CLEANUP_POLICY,
            "source_path": self.source_path,
            "inferred_type": self.inferred_type,
            "action": self.action,
            "blocked": self.blocked,
            "changed": self.changed,
            "removed_keys": list(self.removed_keys),
            "current": {
                "size_bytes": self.current_size,
                "sha256": self.current_sha256,
            },
            "planned": planned,
            "diagnostics": [diagnostic.to_view() for diagnostic in self.diagnostics],
        }


def plan_inferred_type_cleanup(
    content: bytes,
    inferred_type: str,
    *,
    source_path: str = "meta.yaml",
) -> MetadataCleanupDraft:
    """Plan removal of one redundant path-derived `type` entry.

    The planner accepts only an uncommented, top-level, single-line
    `type: <family>` entry whose parsed value exactly matches
    `inferred_type`. It preserves all other source bytes and parses the
    replacement again to prove that removing the entry changes no other YAML
    value.

    Args:
        content (bytes): Stable UTF-8 metadata bytes captured by the caller.
        inferred_type (str): Module family inferred from typed folder ancestry.
        source_path (str): Reader-facing source path used in diagnostics.

    Returns:
        MetadataCleanupDraft: Immutable cleanup action, source and target
            fingerprints, optional replacement bytes, and diagnostics.

    Raises:
        TypeError: If `content` is not bytes.
        ValueError: If `inferred_type` or `source_path` is empty.
    """

    if not isinstance(content, bytes):
        raise TypeError("Metadata cleanup content must be bytes.")
    if not isinstance(inferred_type, str) or not inferred_type.strip():
        raise ValueError("Metadata cleanup inferred_type must be non-empty.")
    if not isinstance(source_path, str) or not source_path.strip():
        raise ValueError("Metadata cleanup source_path must be non-empty.")
    family = inferred_type.strip()
    path = source_path.strip()

    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return _draft(
            content,
            family,
            path,
            action="blocked",
            diagnostic=_diagnostic(
                "module_metadata_cleanup.invalid_utf8",
                f"{path} must be valid UTF-8 before ParaDev can clean it.",
                path,
            ),
        )

    try:
        metadata = _metadata_mapping(text)
    except Exception:
        # HeavenBase deliberately hides the concrete safe-YAML loader and its
        # exception types. User-authored metadata is a fail-closed boundary.
        return _draft(
            content,
            family,
            path,
            action="blocked",
            diagnostic=_diagnostic(
                "module_metadata_cleanup.invalid_yaml",
                f"{path} must contain valid single-document YAML before ParaDev can clean it.",
                path,
            ),
        )
    if metadata is None:
        return _draft(
            content,
            family,
            path,
            action="blocked",
            diagnostic=_diagnostic(
                "module_metadata_cleanup.invalid_mapping",
                f"{path} must contain a YAML mapping before ParaDev can clean it.",
                path,
            ),
        )
    if "type" not in metadata:
        return _draft(content, family, path, action="unchanged")

    lines = content.splitlines(keepends=True)
    simple_lines = [(index, match.group(1).decode("ascii")) for index, line in enumerate(lines) if (match := _SIMPLE_TYPE_LINE.fullmatch(line)) is not None]
    if not simple_lines:
        return _draft(
            content,
            family,
            path,
            action="blocked",
            diagnostic=_diagnostic(
                "module_metadata_cleanup.type_not_simple",
                f"{path} type must be one direct top-level plain scalar before ParaDev can remove it.",
                path,
            ),
        )
    if len(simple_lines) != 1:
        return _draft(
            content,
            family,
            path,
            action="blocked",
            diagnostic=_diagnostic(
                "module_metadata_cleanup.duplicate_type",
                f"{path} contains more than one top-level type entry.",
                path,
            ),
        )

    declared_type = metadata.get("type")
    if not isinstance(declared_type, str):
        return _draft(
            content,
            family,
            path,
            action="blocked",
            diagnostic=_diagnostic(
                "module_metadata_cleanup.type_not_simple",
                f"{path} type must be one direct top-level plain text scalar before ParaDev can remove it.",
                path,
            ),
        )
    if declared_type != family:
        return _draft(
            content,
            family,
            path,
            action="blocked",
            diagnostic=_diagnostic(
                "module_metadata_cleanup.type_mismatch",
                f"{path} type {declared_type!r} does not match inferred type {family!r}.",
                path,
            ),
        )

    if simple_lines[0][1] != family:
        return _draft(
            content,
            family,
            path,
            action="blocked",
            diagnostic=_diagnostic(
                "module_metadata_cleanup.type_not_simple",
                f"{path} type must use one uncommented single-line 'type: {family}' entry before ParaDev can remove it.",
                path,
            ),
        )

    line_index = simple_lines[0][0]
    replacement = b"".join((*lines[:line_index], *lines[line_index + 1 :]))
    expected = dict(metadata)
    del expected["type"]
    if not replacement.strip(_YAML_WHITESPACE):
        return _draft(
            content,
            family,
            path,
            action="remove",
            removed_keys=("type",),
        )
    try:
        replacement_metadata = _metadata_mapping(replacement.decode("utf-8"))
        if replacement_metadata is None and not expected:
            replacement = _append_empty_mapping(content, replacement)
            replacement_metadata = _metadata_mapping(replacement.decode("utf-8"))
        equivalent = replacement_metadata == expected
    except Exception:
        # See the safe-loader boundary above. Any replacement ambiguity blocks
        # the plan rather than escaping as a project-wide cleanup failure.
        equivalent = False
    if not equivalent:
        return _draft(
            content,
            family,
            path,
            action="blocked",
            diagnostic=_diagnostic(
                "module_metadata_cleanup.semantic_change",
                f"Removing the redundant type entry from {path} would change other YAML values.",
                path,
            ),
        )
    return _draft(
        content,
        family,
        path,
        action="update",
        replacement=replacement,
        removed_keys=("type",),
    )


def _metadata_mapping(text: str) -> dict[object, object] | None:
    """Load one YAML mapping through HeavenBase's safe serializer boundary."""

    value = loads_yaml(text)
    return value if isinstance(value, dict) else None


def _append_empty_mapping(content: bytes, replacement: bytes) -> bytes:
    """Retain comments while keeping the remaining YAML a real mapping."""

    if b"\r\n" in content:
        newline = b"\r\n"
    elif b"\r" in content:
        newline = b"\r"
    else:
        newline = b"\n"
    separator = b"" if replacement.endswith((b"\r", b"\n")) else newline
    trailing = newline if content.endswith((b"\r", b"\n")) else b""
    return replacement + separator + b"{}" + trailing


def _diagnostic(code: str, message: str, source_path: str) -> MetadataCleanupDiagnostic:
    return MetadataCleanupDiagnostic(
        code=code,
        message=message,
        source_path=source_path,
    )


def _draft(
    content: bytes,
    inferred_type: str,
    source_path: str,
    *,
    action: MetadataCleanupAction,
    replacement: bytes | None = None,
    removed_keys: tuple[str, ...] = (),
    diagnostic: MetadataCleanupDiagnostic | None = None,
) -> MetadataCleanupDraft:
    if action == "update":
        if replacement is None:
            raise ValueError("Metadata cleanup update requires replacement bytes.")
        target_exists: bool | None = True
        target_size = len(replacement)
        target_sha256 = _sha256(replacement)
        if target_sha256 is None:
            raise ValueError("Metadata cleanup replacement must be valid UTF-8.")
    elif action == "unchanged":
        target_exists = True
        target_size = len(content)
        target_sha256 = _sha256(content)
    elif action == "remove":
        target_exists = False
        target_size = None
        target_sha256 = None
    else:
        target_exists = None
        target_size = None
        target_sha256 = None
    return MetadataCleanupDraft(
        source_path=source_path,
        inferred_type=inferred_type,
        action=action,
        current_size=len(content),
        current_sha256=_sha256(content),
        target_exists=target_exists,
        target_size=target_size,
        target_sha256=target_sha256,
        replacement=replacement,
        removed_keys=removed_keys,
        diagnostics=(diagnostic,) if diagnostic is not None else (),
    )


def _sha256(content: bytes) -> str | None:
    """Hash exact UTF-8 source bytes through HeavenBase's stable hash helper."""

    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return None
    return sha256hash(text)
