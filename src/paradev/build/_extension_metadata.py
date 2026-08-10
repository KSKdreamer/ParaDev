"""Plan and apply hidden project extension metadata migration."""

from __future__ import annotations

import ast
import os
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Literal
from uuid import uuid4

from heavenbase.utils import dumps_yaml, load_yaml

HIDDEN_DESCRIPTOR = Path(".paradev/meta.yaml")
MetadataMoveAction = Literal["move", "remove-duplicate"]


@dataclass(frozen=True, slots=True)
class ExtensionMetadataMove:
    """One exact, resumable extension-descriptor migration."""

    extension: str
    source: Path
    target: Path
    sha256: str
    action: MetadataMoveAction

    def to_view(self, project_root: Path) -> dict[str, str]:
        """Return a JSON-safe project-relative migration row."""

        return {
            "extension": self.extension,
            "action": self.action,
            "source": self.source.relative_to(project_root).as_posix(),
            "target": self.target.relative_to(project_root).as_posix(),
            "sha256": self.sha256,
        }


@dataclass(frozen=True, slots=True)
class ExtensionPublicationDraft:
    """One exact hidden-descriptor publication-metadata rewrite."""

    extension: str
    source: Path
    current_sha256: str
    target_sha256: str
    replacement: bytes

    def to_view(self, project_root: Path) -> dict[str, str]:
        """Return a content-free project-relative migration row."""

        return {
            "extension": self.extension,
            "source": self.source.relative_to(project_root).as_posix(),
            "current_sha256": self.current_sha256,
            "target_sha256": self.target_sha256,
        }


def plan_hidden_extension_metadata(
    project_root: Path,
) -> tuple[ExtensionMetadataMove, ...]:
    """Plan hiding generated HeavenBase descriptors without changing bytes.

    Args:
        project_root: ParaDev project containing an ``extensions`` directory.

    Returns:
        Exact moves needed to leave every extension with only
        ``.paradev/meta.yaml``.

    Raises:
        FileNotFoundError: If the extension root or a descriptor is missing.
        ValueError: If visible and hidden descriptors disagree.
    """

    root = project_root.expanduser().resolve()
    extensions_root = root / "extensions"
    if not extensions_root.is_dir():
        raise FileNotFoundError(
            f"Project extension directory does not exist: {extensions_root}"
        )

    moves: list[ExtensionMetadataMove] = []
    for extension_root in sorted(
        path
        for path in extensions_root.iterdir()
        if path.is_dir() and not path.name.startswith(".")
    ):
        visible = extension_root / "meta.yaml"
        hidden = extension_root / HIDDEN_DESCRIPTOR
        visible_exists = visible.is_file()
        hidden_exists = hidden.is_file()
        if not visible_exists and not hidden_exists:
            raise FileNotFoundError(
                f"Project extension has no descriptor: {extension_root}"
            )
        if hidden_exists and not visible_exists:
            continue

        visible_bytes = visible.read_bytes()
        fingerprint = sha256(visible_bytes).hexdigest()
        if hidden_exists:
            if hidden.read_bytes() != visible_bytes:
                raise ValueError(
                    f"Project extension {extension_root.name!r} has conflicting "
                    "meta.yaml and .paradev/meta.yaml descriptors."
                )
            action: MetadataMoveAction = "remove-duplicate"
        else:
            action = "move"
        moves.append(
            ExtensionMetadataMove(
                extension=extension_root.name,
                source=visible,
                target=hidden,
                sha256=fingerprint,
                action=action,
            )
        )
    return tuple(moves)


def hide_project_extension_metadata(
    project_root: Path,
    *,
    write: bool = False,
) -> tuple[ExtensionMetadataMove, ...]:
    """Plan or apply the hidden extension-descriptor migration.

    Applying a move first creates a same-filesystem hard link at the hidden
    path and only then removes the visible name. A crash can therefore leave
    two byte-identical names but cannot leave the descriptor without a name;
    rerunning the migration removes that safe duplicate.

    Args:
        project_root: ParaDev project containing project-local extensions.
        write: Whether to apply the exact migration plan.

    Returns:
        Planned or applied descriptor moves.

    Raises:
        FileNotFoundError: If an expected source disappears.
        RuntimeError: If a source changes after planning.
        ValueError: If a destination conflicts with the planned bytes.
        OSError: If the filesystem cannot create the safe hard link or remove
            the redundant visible name.
    """

    root = project_root.expanduser().resolve()
    moves = plan_hidden_extension_metadata(root)
    if not write:
        return moves

    for move in moves:
        current = move.source.read_bytes()
        if sha256(current).hexdigest() != move.sha256:
            raise RuntimeError(
                f"Project extension descriptor changed after planning: {move.source}"
            )
        if move.action == "move" and move.target.exists():
            raise ValueError(
                f"Project extension descriptor destination appeared after "
                f"planning: {move.target}"
            )
        if move.action == "remove-duplicate" and (
            not move.target.is_file() or move.target.read_bytes() != current
        ):
            raise ValueError(
                f"Project extension descriptor duplicate changed after "
                f"planning: {move.target}"
            )

    for move in moves:
        if move.action == "move":
            move.target.parent.mkdir(parents=True, exist_ok=True)
            os.link(move.source, move.target)
            if move.target.read_bytes() != move.source.read_bytes():
                move.target.unlink()
                raise RuntimeError(
                    f"Hidden project extension descriptor did not preserve "
                    f"exact bytes: {move.target}"
                )
        move.source.unlink()
    return moves


def plan_extension_publication_metadata(
    project_root: Path,
) -> tuple[ExtensionPublicationDraft, ...]:
    """Plan moving publication replacements into Registry item metadata.

    The planner recognizes the former compiler constructor keyword and former
    inline family declaration only as one-shot migration input. It writes the
    canonical state to
    ``meta.publication.replaces_families`` on the owning
    ``paradev_build_family`` item.

    Args:
        project_root: ParaDev project containing project-local extensions.

    Returns:
        Exact hidden-descriptor rewrites.

    Raises:
        FileNotFoundError: If an extension descriptor is missing.
        TypeError: If a descriptor or declaration has an invalid shape.
        ValueError: If migration sources conflict or Python declarations are
            not literal string sequences.
    """

    root = project_root.expanduser().resolve()
    extensions_root = root / "extensions"
    if not extensions_root.is_dir():
        raise FileNotFoundError(
            f"Project extension directory does not exist: {extensions_root}"
        )

    drafts: list[ExtensionPublicationDraft] = []
    for extension_root in sorted(
        path
        for path in extensions_root.iterdir()
        if path.is_dir() and not path.name.startswith(".")
    ):
        descriptor_path = _descriptor_path(extension_root)
        raw = load_yaml(str(descriptor_path), strict=True)
        if not isinstance(raw, dict):
            raise TypeError(
                f"Project extension descriptor must be a mapping: {descriptor_path}"
            )
        items = raw.get("items")
        if not isinstance(items, list):
            raise TypeError(
                f"Project extension descriptor items must be a list: {descriptor_path}"
            )
        family_items = [
            item
            for item in items
            if isinstance(item, dict) and item.get("kind") == "paradev_build_family"
        ]
        python_replacements = _python_publication_replacements(
            extension_root / "__init__.py"
        )
        if python_replacements and len(family_items) != 1:
            raise ValueError(
                f"Project extension {extension_root.name!r} has Python "
                "publication replacements but does not own exactly one build "
                "family item."
            )

        changed = False
        for item in family_items:
            meta = item.get("meta")
            if not isinstance(meta, dict):
                raise TypeError(
                    f"Project extension build-family metadata must be a "
                    f"mapping: {descriptor_path}"
                )
            declaration_replacements = _legacy_declaration_replacements(
                meta,
                descriptor_path,
            )
            published_replacements = _published_replacements(
                meta,
                descriptor_path,
            )
            candidates = [
                values
                for values in (
                    declaration_replacements,
                    published_replacements,
                    python_replacements,
                )
                if values
            ]
            if not candidates:
                continue
            replacements = candidates[0]
            if any(values != replacements for values in candidates[1:]):
                raise ValueError(
                    f"Project extension {extension_root.name!r} has "
                    "conflicting publication replacement declarations."
                )
            publication = meta.get("publication")
            if publication != {"replaces_families": list(replacements)}:
                meta["publication"] = {"replaces_families": list(replacements)}
                changed = True
            if _remove_legacy_declaration_replacements(meta):
                changed = True
        if not changed:
            continue

        current = descriptor_path.read_bytes()
        replacement = f"{dumps_yaml(raw, sort_keys=False).rstrip()}\n".encode()
        drafts.append(
            ExtensionPublicationDraft(
                extension=extension_root.name,
                source=descriptor_path,
                current_sha256=sha256(current).hexdigest(),
                target_sha256=sha256(replacement).hexdigest(),
                replacement=replacement,
            )
        )
    return tuple(drafts)


def migrate_extension_publication_metadata(
    project_root: Path,
    *,
    write: bool = False,
) -> tuple[ExtensionPublicationDraft, ...]:
    """Plan or apply descriptor-owned publication replacement metadata.

    Args:
        project_root: ParaDev project containing project-local extensions.
        write: Whether to atomically replace each exact planned descriptor.

    Returns:
        Planned or applied descriptor drafts.

    Raises:
        RuntimeError: If a descriptor changes after planning.
        OSError: If an atomic descriptor replacement cannot be published.
        TypeError: If extension metadata has an invalid shape.
        ValueError: If migration sources conflict.
    """

    root = project_root.expanduser().resolve()
    drafts = plan_extension_publication_metadata(root)
    if not write:
        return drafts
    for draft in drafts:
        if sha256(draft.source.read_bytes()).hexdigest() != (draft.current_sha256):
            raise RuntimeError(
                f"Project extension descriptor changed after planning: {draft.source}"
            )
    for draft in drafts:
        temporary = draft.source.with_name(f".{draft.source.name}.{uuid4().hex}.tmp")
        try:
            temporary.write_bytes(draft.replacement)
            temporary.replace(draft.source)
        finally:
            temporary.unlink(missing_ok=True)
    return drafts


def _descriptor_path(extension_root: Path) -> Path:
    visible = extension_root / "meta.yaml"
    hidden = extension_root / HIDDEN_DESCRIPTOR
    if visible.is_file() and hidden.is_file():
        raise ValueError(
            f"{extension_root} contains both meta.yaml and .paradev/meta.yaml."
        )
    if hidden.is_file():
        return hidden
    if visible.is_file():
        return visible
    raise FileNotFoundError(f"{extension_root} has no project extension descriptor.")


def _python_publication_replacements(path: Path) -> tuple[str, ...]:
    if not path.is_file():
        return ()
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    claims: list[tuple[str, ...]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        for keyword in node.keywords:
            if keyword.arg != "retired_families":
                continue
            try:
                raw = ast.literal_eval(keyword.value)
            except (TypeError, ValueError) as error:
                raise ValueError(
                    f"{path} retired_families must be a literal string "
                    "sequence before migration."
                ) from error
            claims.append(
                _replacement_sequence(
                    raw,
                    f"{path} retired_families",
                )
            )
    if not claims:
        return ()
    first = claims[0]
    if any(claim != first for claim in claims[1:]):
        raise ValueError(f"{path} contains conflicting retired_families declarations.")
    return first


def _legacy_declaration_replacements(
    meta: dict[str, object],
    source: Path,
) -> tuple[str, ...]:
    definition = meta.get("definition")
    if not isinstance(definition, dict):
        return ()
    declaration = definition.get("declaration")
    if not isinstance(declaration, dict):
        return ()
    raw = declaration.get("retired_families")
    if raw is None:
        return ()
    return _replacement_sequence(
        raw,
        f"{source} declaration.retired_families",
    )


def _remove_legacy_declaration_replacements(
    meta: dict[str, object],
) -> bool:
    definition = meta.get("definition")
    if not isinstance(definition, dict):
        return False
    declaration = definition.get("declaration")
    if not isinstance(declaration, dict):
        return False
    return declaration.pop("retired_families", None) is not None


def _published_replacements(
    meta: dict[str, object],
    source: Path,
) -> tuple[str, ...]:
    publication = meta.get("publication")
    if publication is None:
        return ()
    if not isinstance(publication, dict):
        raise TypeError(f"{source} meta.publication must be a mapping.")
    unknown = set(publication) - {"replaces_families"}
    if unknown:
        raise ValueError(
            f"{source} meta.publication has unsupported fields {sorted(unknown)!r}."
        )
    return _replacement_sequence(
        publication.get("replaces_families"),
        f"{source} meta.publication.replaces_families",
    )


def _replacement_sequence(raw: object, label: str) -> tuple[str, ...]:
    if not isinstance(raw, (list, tuple)) or not raw:
        raise TypeError(f"{label} must be a non-empty list of strings.")
    values: list[str] = []
    for value in raw:
        if not isinstance(value, str) or not value.strip():
            raise TypeError(f"{label} must be a non-empty list of strings.")
        values.append(value)
    if len(values) != len(set(values)):
        raise ValueError(f"{label} must not contain duplicates.")
    if any(value != value.strip() for value in values):
        raise ValueError(f"{label} values must not have surrounding whitespace.")
    return tuple(sorted(values))


__all__ = [
    "ExtensionMetadataMove",
    "ExtensionPublicationDraft",
    "hide_project_extension_metadata",
    "migrate_extension_publication_metadata",
    "plan_extension_publication_metadata",
    "plan_hidden_extension_metadata",
]
