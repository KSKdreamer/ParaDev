"""Retained Win32 transactions for source-module directory authoring.

This module is intentionally private.  The public SDK owns diagnostics and
catalog changes; this adapter owns the smallest Win32-specific filesystem
transaction needed by those workflows.
"""

from __future__ import annotations

import errno
import hashlib
import logging
import re
import unicodedata
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Protocol
from uuid import uuid4

from paradev._win32_fs import (
    Win32DirectoryAuthority,
    Win32FileGuard,
    Win32FileMetadata,
    Win32FileSnapshot,
    Win32FilesystemUnavailable,
    Win32UnsafePathError,
)
from paradev.portable_paths import (
    portable_path_identity,
    windows_portable_component_error,
)

logger = logging.getLogger(__name__)

_TRANSACTION_ROOT = (".paradev", "module-transactions")
_TRASH_ROOT = (".paradev", "module-trash")
_QUARANTINE_PATTERN = re.compile(r"\Amodule-[0-9a-f]{32}-([0-9a-f]+)-([0-9a-f]+)-([0-9a-f]{64})\Z")


class WindowsModuleMutationUnavailable(OSError):
    """Raised before mutation when retained Win32 authoring is unavailable."""


class WindowsScaffoldRollbackIncomplete(OSError):
    """Raised when a scaffold transaction must remain available for recovery."""

    def __init__(self, message: str, recovery_path: Path) -> None:
        super().__init__(message)
        self.recovery_path = recovery_path


class _WindowsModuleAuthority(Protocol):
    """The low-level retained authority consumed by module transactions."""

    identity: tuple[int, int]
    path: Path

    def close(self) -> None: ...

    def verify_path(self) -> None: ...

    def directory_names(self, parts: tuple[str, ...] = ()) -> tuple[str, ...]: ...

    def create_directory(
        self,
        parts: tuple[str, ...],
        *,
        exist_ok: bool = False,
    ) -> tuple[Win32FileMetadata, bool]: ...

    def guarded_move_entry(
        self,
        source_parts: tuple[str, ...],
        target_parts: tuple[str, ...],
        *,
        guard: Win32FileGuard,
        create_target_parent: bool = False,
        expected_target_parent_identity: tuple[int, int] | None = None,
    ) -> Win32FileSnapshot: ...

    def remove_empty_directory(
        self,
        parts: tuple[str, ...],
        *,
        expected_identity: tuple[int, int],
    ) -> bool: ...

    def remove_directory_tree(
        self,
        parts: tuple[str, ...],
        *,
        expected_identity: tuple[int, int],
    ) -> bool: ...

    def read_file_snapshot(
        self,
        parts: tuple[str, ...],
        *,
        max_bytes: int | None = None,
    ) -> Win32FileSnapshot | None: ...

    def entry_metadata(
        self,
        parts: tuple[str, ...],
    ) -> Win32FileMetadata | None: ...

    def write_bytes_snapshot(
        self,
        parts: tuple[str, ...],
        payload: bytes,
        *,
        replace: bool,
        create_parent: bool = False,
    ) -> tuple[tuple[int, int], Win32FileSnapshot]: ...

    def guarded_remove_file(
        self,
        parts: tuple[str, ...],
        *,
        guard: Win32FileGuard,
        missing_ok: bool = False,
    ) -> tuple[tuple[int, int], Win32FileSnapshot | None]: ...


_AuthorityOpener = Callable[[Path], _WindowsModuleAuthority]


@dataclass(frozen=True, slots=True)
class _RenderedFile:
    """One validated rendered file and its normalized bytes."""

    parts: tuple[str, ...]
    payload: bytes


@dataclass(slots=True)
class _OwnedTransaction:
    """Exact entries currently owned below one private transaction root."""

    parts: tuple[str, ...]
    root_identity: tuple[int, int]
    directories: dict[tuple[str, ...], tuple[int, int]] = field(default_factory=dict)
    files: dict[tuple[str, ...], Win32FileSnapshot] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.directories[self.parts] = self.root_identity

    def add_directory(
        self,
        parts: tuple[str, ...],
        metadata: Win32FileMetadata,
    ) -> None:
        self.directories[parts] = metadata.identity

    def add_file(
        self,
        parts: tuple[str, ...],
        snapshot: Win32FileSnapshot,
    ) -> None:
        self.files[parts] = snapshot

    def discard_file(self, parts: tuple[str, ...]) -> None:
        self.files.pop(parts, None)

    def discard_tree(self, parts: tuple[str, ...]) -> None:
        self.directories = {path: identity for path, identity in self.directories.items() if not _is_at_or_below(path, parts)}
        self.files = {path: snapshot for path, snapshot in self.files.items() if not _is_at_or_below(path, parts)}


@dataclass(frozen=True, slots=True)
class _TreeInventory:
    """Stable identities and contents for one retained directory tree."""

    directories: Mapping[tuple[str, ...], Win32FileMetadata]
    files: Mapping[tuple[str, ...], Win32FileSnapshot]

    @property
    def root_metadata(self) -> Win32FileMetadata:
        return self.directories[()]


@dataclass(slots=True)
class _StagedTree:
    """One staged module directory and its exact authored inventory."""

    stage_parts: tuple[str, ...]
    target_parts: tuple[str, ...]
    inventory: _TreeInventory
    move_snapshot: Win32FileSnapshot
    installed: bool = False


@dataclass(slots=True)
class _ForceInstall:
    """One reversible force-write file installation."""

    stage_parts: tuple[str, ...]
    target_parts: tuple[str, ...]
    backup_parts: tuple[str, ...]
    stage_parent_identity: tuple[int, int]
    stage_snapshot: Win32FileSnapshot
    target_parent_identity: tuple[int, int]
    original_snapshot: Win32FileSnapshot | None
    backup_snapshot: Win32FileSnapshot | None = None
    installed_snapshot: Win32FileSnapshot | None = None


def write_scaffold_files_windows(
    project_root: Path,
    source_root: Path,
    family: str,
    object_id: str,
    folder_name: str,
    rendered_files: Sequence[Mapping[str, object]],
    force: bool,
    *,
    container: str = "modules",
    _authority_opener: _AuthorityOpener | None = None,
) -> None:
    """Install one source resource scaffold through a retained Win32 transaction."""

    _require_source_within_project(project_root, source_root)
    container = _exact_component(container, label="source container")
    family = _exact_component(family, label="module family")
    object_id = _exact_component(object_id, label="module object id")
    folder_name = _exact_component(folder_name, label="module folder")
    rendered = _rendered_files(rendered_files)
    authority = _open_authority(source_root, _authority_opener)
    mutated = False
    transaction: _OwnedTransaction | None = None
    try:
        family_parts = (container, family)
        target_parts = (*family_parts, folder_name)
        _require_exact_existing_directory_path(
            authority,
            family_parts,
            missing_ok=True,
        )
        _require_no_module_alias(
            authority,
            family_parts,
            object_id=object_id,
            allowed_names=(folder_name,),
        )
        target_metadata = authority.entry_metadata(target_parts)
        if target_metadata is not None and not target_metadata.is_directory:
            raise OSError(f"Module scaffold target is not a directory: {folder_name}")
        if target_metadata is not None:
            _require_exact_directory_name(authority, family_parts, folder_name)

        mutated = True
        transaction = _new_transaction(
            authority,
            prefix=f"{family}-{object_id}",
        )
        if target_metadata is None:
            staged = _stage_module_tree(
                authority,
                transaction,
                stage_name="module.stage",
                target_parts=target_parts,
                rendered=rendered,
            )
            _install_staged_trees(
                authority,
                transaction,
                [staged],
                aliases=[(family_parts, object_id, folder_name)],
            )
        else:
            _force_install_rendered_files(
                authority,
                transaction,
                module_parts=target_parts,
                rendered=rendered,
                allow_overwrite=force,
                expected_module_identity=target_metadata.identity,
            )
            _require_no_module_alias(
                authority,
                family_parts,
                object_id=object_id,
                allowed_names=(folder_name,),
            )
            authority.verify_path()
        _cleanup_transaction_best_effort(authority, transaction)
    except BaseException as error:
        if isinstance(error, (WindowsScaffoldRollbackIncomplete, WindowsModuleMutationUnavailable)):
            raise
        if transaction is not None:
            _cleanup_transaction_best_effort(authority, transaction)
        if isinstance(error, (Win32FilesystemUnavailable, Win32UnsafePathError)):
            if mutated:
                raise OSError(
                    errno.EAGAIN,
                    f"Windows scaffold path changed during mutation: {error}",
                ) from error
            raise WindowsModuleMutationUnavailable(str(error)) from error
        raise
    finally:
        authority.close()


def write_scaffold_batch_windows(
    project_root: Path,
    source_root: Path,
    scaffolds: Sequence[tuple[str, str, str, Sequence[Mapping[str, object]]]],
    *,
    validate: Callable[[], None] | None = None,
    _authority_opener: _AuthorityOpener | None = None,
) -> None:
    """Create several new modules as one staged, reversible transaction."""

    if not scaffolds:
        return
    _require_source_within_project(project_root, source_root)
    prepared = _prepared_batch(scaffolds)
    authority = _open_authority(source_root, _authority_opener)
    mutated = False
    transaction: _OwnedTransaction | None = None
    try:
        aliases = [(("modules", family), object_id, folder_name) for family, object_id, folder_name, _rendered in prepared]
        _preflight_new_targets(authority, aliases)
        mutated = True
        transaction = _new_transaction(authority, prefix="batch")
        staged = [
            _stage_module_tree(
                authority,
                transaction,
                stage_name=f"module-{index:06d}.stage",
                target_parts=("modules", family, folder_name),
                rendered=rendered,
            )
            for index, (family, _object_id, folder_name, rendered) in enumerate(prepared)
        ]
        _install_staged_trees(
            authority,
            transaction,
            staged,
            aliases=aliases,
            validate=validate,
        )
        _cleanup_transaction_best_effort(authority, transaction)
    except BaseException as error:
        if isinstance(error, (WindowsScaffoldRollbackIncomplete, WindowsModuleMutationUnavailable)):
            raise
        if transaction is not None:
            _cleanup_transaction_best_effort(authority, transaction)
        if isinstance(error, (Win32FilesystemUnavailable, Win32UnsafePathError)):
            if mutated:
                raise OSError(
                    errno.EAGAIN,
                    f"Windows scaffold batch path changed during mutation: {error}",
                ) from error
            raise WindowsModuleMutationUnavailable(str(error)) from error
        raise
    finally:
        authority.close()


def rename_module_directory_windows(
    source_root: Path,
    family: str,
    source_name: str,
    target_name: str,
    target_object_id: str,
    *,
    container: str = "modules",
    expected_source_identity: tuple[int, int] | None = None,
    _authority_opener: _AuthorityOpener | None = None,
) -> None:
    """Rename one exact Registry-container folder with guarded rollback."""

    container = _exact_component(container, label="source container")
    if container not in {"modules", "collections"}:
        raise ValueError("Source container must be 'modules' or 'collections'.")
    family = _exact_component(family, label="module family")
    source_name = _exact_component(source_name, label="source module folder")
    target_name = _exact_component(target_name, label="target module folder")
    target_object_id = _exact_component(
        target_object_id,
        label="target module object id",
    )
    authority = _open_authority(source_root, _authority_opener)
    moved = False
    family_parts = (container, family)
    source_parts = (*family_parts, source_name)
    target_parts = (*family_parts, target_name)
    try:
        _require_exact_existing_directory_path(
            authority,
            family_parts,
            missing_ok=False,
        )
        _require_exact_directory_name(authority, family_parts, source_name)
        source_metadata = _require_directory(authority, source_parts)
        if expected_source_identity is not None and source_metadata.identity != expected_source_identity:
            raise OSError(
                errno.EAGAIN,
                f"Module rename source identity changed: {source_name}",
            )
        family_metadata = _require_directory(authority, family_parts)
        _require_no_module_alias(
            authority,
            family_parts,
            object_id=target_object_id,
            allowed_names=(source_name,),
        )
        _require_missing_or_same_entry(
            authority,
            target_parts,
            source_metadata,
            target_name,
        )
        expected = _require_entry_snapshot(
            authority,
            source_parts,
            label=f"module rename source {source_name}",
        )
        moved_snapshot = authority.guarded_move_entry(
            source_parts,
            target_parts,
            guard=_snapshot_guard(
                family_metadata.identity,
                expected,
                label=f"module rename source {source_name}",
            ),
            expected_target_parent_identity=family_metadata.identity,
        )
        moved = True
        try:
            _require_same_snapshot(
                expected,
                moved_snapshot,
                label=f"module rename source {source_name}",
            )
            _require_entry_snapshot_matches(
                authority,
                target_parts,
                moved_snapshot,
                label=f"module rename target {target_name}",
            )
            _require_exact_directory_name(authority, family_parts, target_name)
            _require_no_module_alias(
                authority,
                family_parts,
                object_id=target_object_id,
                allowed_names=(target_name,),
            )
            authority.verify_path()
        except BaseException as error:
            try:
                authority.guarded_move_entry(
                    target_parts,
                    source_parts,
                    guard=_snapshot_guard(
                        family_metadata.identity,
                        moved_snapshot,
                        label=f"module rename rollback {target_name}",
                    ),
                    expected_target_parent_identity=family_metadata.identity,
                )
            except BaseException as rollback_error:
                raise OSError(
                    errno.EAGAIN,
                    "Module rename changed concurrently and rollback was " f"incomplete: {rollback_error}",
                ) from error
            moved = False
            raise OSError(
                errno.EAGAIN,
                f"Module rename changed concurrently and was rolled back: {error}",
            ) from error
    except (Win32FilesystemUnavailable, Win32UnsafePathError) as error:
        if moved:
            raise OSError(
                errno.EAGAIN,
                f"Windows module rename path changed during mutation: {error}",
            ) from error
        raise WindowsModuleMutationUnavailable(str(error)) from error
    finally:
        authority.close()


def remove_module_directory_windows(
    source_root: Path,
    family: str,
    module_name: str,
    *,
    _authority_opener: _AuthorityOpener | None = None,
) -> tuple[str, Path]:
    """Move one module tree into an identity-bound project-local quarantine."""

    family = _exact_component(family, label="module family")
    module_name = _exact_component(module_name, label="module folder")
    authority = _open_authority(source_root, _authority_opener)
    moved = False
    mutated = False
    family_parts = ("modules", family)
    source_parts = (*family_parts, module_name)
    try:
        _require_exact_existing_directory_path(
            authority,
            family_parts,
            missing_ok=False,
        )
        _require_exact_directory_name(authority, family_parts, module_name)
        inventory = _capture_tree(authority, source_parts)
        family_metadata = _require_directory(authority, family_parts)
        digest = _inventory_digest(inventory)
        root_identity = inventory.root_metadata.identity
        quarantine_name = f"module-{uuid4().hex}-{root_identity[0]:x}-{root_identity[1]:x}-{digest}"
        quarantine_parts = (*_TRASH_ROOT, quarantine_name)
        mutated = True
        _ensure_directory_chain(authority, _TRASH_ROOT)
        trash_metadata = _require_directory(authority, _TRASH_ROOT)
        source_snapshot = _require_entry_snapshot(
            authority,
            source_parts,
            label=f"module removal source {module_name}",
        )
        moved_snapshot = authority.guarded_move_entry(
            source_parts,
            quarantine_parts,
            guard=_snapshot_guard(
                family_metadata.identity,
                source_snapshot,
                label=f"module removal source {module_name}",
            ),
            expected_target_parent_identity=trash_metadata.identity,
        )
        moved = True
        try:
            _require_same_snapshot(
                source_snapshot,
                moved_snapshot,
                label=f"module removal source {module_name}",
            )
            _require_tree(authority, quarantine_parts, inventory)
            authority.verify_path()
        except BaseException as error:
            trash_metadata = _require_directory(authority, _TRASH_ROOT)
            try:
                authority.guarded_move_entry(
                    quarantine_parts,
                    source_parts,
                    guard=_snapshot_guard(
                        trash_metadata.identity,
                        moved_snapshot,
                        label=f"module removal rollback {quarantine_name}",
                    ),
                    expected_target_parent_identity=family_metadata.identity,
                )
            except BaseException as rollback_error:
                quarantine_path = source_root.joinpath(
                    *_TRASH_ROOT,
                    quarantine_name,
                )
                raise OSError(
                    errno.EAGAIN,
                    "Module removal changed concurrently and rollback was " f"incomplete; recovery remains at {quarantine_path}: " f"{rollback_error}",
                ) from error
            moved = False
            raise OSError(
                errno.EAGAIN,
                f"Module removal changed concurrently and was rolled back: {error}",
            ) from error
        return (
            quarantine_name,
            source_root.joinpath(*quarantine_parts),
        )
    except (Win32FilesystemUnavailable, Win32UnsafePathError) as error:
        if moved or mutated:
            raise OSError(
                errno.EAGAIN,
                f"Windows module removal path changed during mutation: {error}",
            ) from error
        raise WindowsModuleMutationUnavailable(str(error)) from error
    finally:
        authority.close()


def cleanup_module_quarantine_windows(
    source_root: Path,
    quarantine_name: str,
    quarantine_path: Path,
    *,
    _authority_opener: _AuthorityOpener | None = None,
) -> tuple[Path | None, str]:
    """Delete an unchanged module quarantine, or return its pending state."""

    try:
        quarantine_name = _exact_component(
            quarantine_name,
            label="module quarantine",
        )
        expected_path = source_root.joinpath(*_TRASH_ROOT, quarantine_name)
        if quarantine_path != expected_path:
            raise ValueError("Module quarantine path does not match its exact project-local " f"location: {quarantine_path}")
        expected_identity, expected_digest = _quarantine_expectation(quarantine_name)
        authority = _open_authority(source_root, _authority_opener)
    except BaseException as error:
        return quarantine_path, str(error)
    quarantine_parts = (*_TRASH_ROOT, quarantine_name)
    try:
        metadata = authority.entry_metadata(quarantine_parts)
        if metadata is None:
            return None, ""
        if not metadata.is_directory or metadata.identity != expected_identity:
            raise OSError("Module quarantine identity changed before cleanup; it was preserved.")
        inventory = _capture_tree(authority, quarantine_parts)
        if _inventory_digest(inventory) != expected_digest:
            raise OSError("Module quarantine contents changed before cleanup; they were " "preserved.")
        _remove_inventory_exact(
            authority,
            quarantine_parts,
            inventory,
        )
        authority.verify_path()
        return None, ""
    except BaseException as error:
        return quarantine_path, str(error)
    finally:
        authority.close()


def _open_authority(
    source_root: Path,
    opener: _AuthorityOpener | None,
) -> _WindowsModuleAuthority:
    selected = opener or _open_native_authority
    try:
        return selected(source_root)
    except (Win32FilesystemUnavailable, Win32UnsafePathError) as error:
        raise WindowsModuleMutationUnavailable(str(error)) from error


def _open_native_authority(source_root: Path) -> _WindowsModuleAuthority:
    return Win32DirectoryAuthority.open(source_root, create=False)


def _new_transaction(
    authority: _WindowsModuleAuthority,
    *,
    prefix: str,
) -> _OwnedTransaction:
    _ensure_directory_chain(authority, _TRANSACTION_ROOT)
    safe_prefix = "".join(character if character.isalnum() or character in {"-", "_"} else "-" for character in prefix)[:64].strip("-") or "module"
    name = f"{safe_prefix}-{uuid4().hex}.txn"
    parts = (*_TRANSACTION_ROOT, name)
    metadata, created = authority.create_directory(parts, exist_ok=False)
    if not created:
        raise FileExistsError(f"Windows scaffold transaction already exists: {name}")
    if not metadata.is_directory:
        raise OSError(f"Windows scaffold transaction is not a directory: {name}")
    return _OwnedTransaction(parts=parts, root_identity=metadata.identity)


def _stage_module_tree(
    authority: _WindowsModuleAuthority,
    transaction: _OwnedTransaction,
    *,
    stage_name: str,
    target_parts: tuple[str, ...],
    rendered: Sequence[_RenderedFile],
) -> _StagedTree:
    stage_parts = (*transaction.parts, stage_name)
    stage_metadata, created = authority.create_directory(
        stage_parts,
        exist_ok=False,
    )
    if not created or not stage_metadata.is_directory:
        raise FileExistsError(f"Windows scaffold stage already exists: {stage_name}")
    transaction.add_directory(stage_parts, stage_metadata)

    for item in rendered:
        for index in range(1, len(item.parts)):
            directory_parts = (*stage_parts, *item.parts[:index])
            if directory_parts in transaction.directories:
                continue
            metadata, directory_created = authority.create_directory(
                directory_parts,
                exist_ok=False,
            )
            if not directory_created or not metadata.is_directory:
                raise FileExistsError("Windows scaffold stage directory already exists: " f"{'/'.join(item.parts[:index])}")
            transaction.add_directory(directory_parts, metadata)
        file_parts = (*stage_parts, *item.parts)
        parent_identity, snapshot = authority.write_bytes_snapshot(
            file_parts,
            item.payload,
            replace=False,
        )
        transaction.add_file(file_parts, snapshot)
        expected_parent = transaction.directories[file_parts[:-1]]
        if parent_identity != expected_parent:
            raise OSError("Windows scaffold stage parent changed while writing: " f"{'/'.join(item.parts)}")

    _require_owned_transaction(authority, transaction)
    inventory = _capture_tree(authority, stage_parts)
    move_snapshot = _require_entry_snapshot(
        authority,
        stage_parts,
        label=f"module stage {stage_name}",
    )
    return _StagedTree(
        stage_parts=stage_parts,
        target_parts=target_parts,
        inventory=inventory,
        move_snapshot=move_snapshot,
    )


def _install_staged_trees(
    authority: _WindowsModuleAuthority,
    transaction: _OwnedTransaction,
    staged: Sequence[_StagedTree],
    *,
    aliases: Sequence[tuple[tuple[str, ...], str, str]],
    validate: Callable[[], None] | None = None,
) -> None:
    _preflight_new_targets(authority, aliases)
    for family_parts, _object_id, _folder_name in aliases:
        _ensure_directory_chain(authority, family_parts)
    _preflight_new_targets(authority, aliases)

    try:
        for state in staged:
            _require_tree(authority, state.stage_parts, state.inventory)
            source_parent = _require_directory(
                authority,
                state.stage_parts[:-1],
            )
            target_parent = _require_directory(
                authority,
                state.target_parts[:-1],
            )
            moved = authority.guarded_move_entry(
                state.stage_parts,
                state.target_parts,
                guard=_snapshot_guard(
                    source_parent.identity,
                    state.move_snapshot,
                    label=f"module stage {state.stage_parts[-1]}",
                ),
                expected_target_parent_identity=target_parent.identity,
            )
            transaction.discard_tree(state.stage_parts)
            state.installed = True
            _require_same_snapshot(
                state.move_snapshot,
                moved,
                label=f"module stage {state.stage_parts[-1]}",
            )

        for state in staged:
            _require_tree(authority, state.target_parts, state.inventory)
        for family_parts, object_id, folder_name in aliases:
            _require_exact_directory_name(
                authority,
                family_parts,
                folder_name,
            )
            _require_no_module_alias(
                authority,
                family_parts,
                object_id=object_id,
                allowed_names=(folder_name,),
            )
        authority.verify_path()
        if validate is not None:
            validate()
    except BaseException as error:
        rollback_errors = _rollback_staged_trees(
            authority,
            transaction,
            staged,
        )
        if rollback_errors:
            _raise_rollback_incomplete(
                transaction,
                rollback_errors,
                source_root=authority.path,
                cause=error,
            )
        _cleanup_transaction_best_effort(authority, transaction)
        raise


def _rollback_staged_trees(
    authority: _WindowsModuleAuthority,
    transaction: _OwnedTransaction,
    staged: Sequence[_StagedTree],
) -> list[BaseException]:
    errors: list[BaseException] = []
    for state in reversed(staged):
        if not state.installed:
            continue
        try:
            _require_tree(authority, state.target_parts, state.inventory)
            target_parent = _require_directory(
                authority,
                state.target_parts[:-1],
            )
            moved = authority.guarded_move_entry(
                state.target_parts,
                state.stage_parts,
                guard=_snapshot_guard(
                    target_parent.identity,
                    state.move_snapshot,
                    label=f"module rollback {state.target_parts[-1]}",
                ),
                expected_target_parent_identity=transaction.root_identity,
            )
            _require_same_snapshot(
                state.move_snapshot,
                moved,
                label=f"module rollback {state.target_parts[-1]}",
            )
            _track_inventory(
                transaction,
                state.stage_parts,
                state.inventory,
            )
            _require_tree(authority, state.stage_parts, state.inventory)
            state.installed = False
        except BaseException as rollback_error:
            errors.append(rollback_error)
    return errors


def _force_install_rendered_files(
    authority: _WindowsModuleAuthority,
    transaction: _OwnedTransaction,
    *,
    module_parts: tuple[str, ...],
    rendered: Sequence[_RenderedFile],
    allow_overwrite: bool,
    expected_module_identity: tuple[int, int],
) -> None:
    installs: list[_ForceInstall] = []
    created_directories: list[tuple[tuple[str, ...], tuple[int, int]]] = []
    try:
        _require_directory_identity(
            authority,
            module_parts,
            expected_module_identity,
            label="force scaffold module",
        )
        for index, item in enumerate(rendered):
            stage_parts = (*transaction.parts, f"{index:06d}.stage")
            stage_parent, stage_snapshot = authority.write_bytes_snapshot(
                stage_parts,
                item.payload,
                replace=False,
            )
            transaction.add_file(stage_parts, stage_snapshot)
            if stage_parent != transaction.root_identity:
                raise OSError(f"Windows force stage parent changed: {stage_parts[-1]}")
            target_parts = (*module_parts, *item.parts)
            _ensure_target_parent_directories(
                authority,
                target_parts[:-1],
                created_directories,
            )
            target_parent = _require_directory(
                authority,
                target_parts[:-1],
            )
            target_metadata = authority.entry_metadata(target_parts)
            if target_metadata is not None and target_metadata.is_directory:
                raise OSError("Windows force scaffold target is a directory: " f"{'/'.join(item.parts)}")
            original = authority.read_file_snapshot(target_parts) if target_metadata is not None else None
            if target_metadata is not None and original is None:
                raise OSError("Windows force scaffold target changed while it was read: " f"{'/'.join(item.parts)}")
            if original is not None:
                _require_metadata_snapshot(
                    target_metadata,
                    original,
                    label=f"force target {'/'.join(item.parts)}",
                )
                if not allow_overwrite:
                    raise FileExistsError(f"Scaffold target already exists: {'/'.join(item.parts)}")
            installs.append(
                _ForceInstall(
                    stage_parts=stage_parts,
                    target_parts=target_parts,
                    backup_parts=(
                        *transaction.parts,
                        f"{index:06d}.backup",
                    ),
                    stage_parent_identity=stage_parent,
                    stage_snapshot=stage_snapshot,
                    target_parent_identity=target_parent.identity,
                    original_snapshot=original,
                )
            )

        for install in installs:
            if install.original_snapshot is not None:
                _require_directory_identity(
                    authority,
                    module_parts,
                    expected_module_identity,
                    label="force scaffold module",
                )
                backup = authority.guarded_move_entry(
                    install.target_parts,
                    install.backup_parts,
                    guard=_snapshot_guard(
                        install.target_parent_identity,
                        install.original_snapshot,
                        label=f"force backup {install.target_parts[-1]}",
                    ),
                    expected_target_parent_identity=transaction.root_identity,
                )
                install.backup_snapshot = backup
                transaction.add_file(install.backup_parts, backup)
                _require_same_snapshot(
                    install.original_snapshot,
                    backup,
                    label=f"force backup {install.target_parts[-1]}",
                )
            _require_directory_identity(
                authority,
                module_parts,
                expected_module_identity,
                label="force scaffold module",
            )
            installed = authority.guarded_move_entry(
                install.stage_parts,
                install.target_parts,
                guard=_snapshot_guard(
                    install.stage_parent_identity,
                    install.stage_snapshot,
                    label=f"force stage {install.target_parts[-1]}",
                ),
                expected_target_parent_identity=install.target_parent_identity,
            )
            install.installed_snapshot = installed
            transaction.discard_file(install.stage_parts)
            _require_same_snapshot(
                install.stage_snapshot,
                installed,
                label=f"force stage {install.target_parts[-1]}",
            )

        _require_directory_identity(
            authority,
            module_parts,
            expected_module_identity,
            label="force scaffold module",
        )
        for install in installs:
            current = authority.read_file_snapshot(install.target_parts)
            _require_same_snapshot(
                install.stage_snapshot,
                current,
                label=f"force install {install.target_parts[-1]}",
            )
        authority.verify_path()
        _require_directory_identity(
            authority,
            module_parts,
            expected_module_identity,
            label="force scaffold module",
        )
    except BaseException as error:
        rollback_errors = _rollback_force_installs(
            authority,
            transaction,
            installs,
            created_directories,
        )
        if rollback_errors:
            _raise_rollback_incomplete(
                transaction,
                rollback_errors,
                source_root=authority.path,
                cause=error,
            )
        _cleanup_transaction_best_effort(authority, transaction)
        raise

    cleanup_errors = _discard_force_backups(
        authority,
        transaction,
        installs,
    )
    if cleanup_errors:
        logger.warning(
            "Committed Windows scaffold retained original-file recovery data at %s: %s",
            authority.path.joinpath(*transaction.parts),
            "; ".join(str(error) for error in cleanup_errors),
        )


def _rollback_force_installs(
    authority: _WindowsModuleAuthority,
    transaction: _OwnedTransaction,
    installs: Sequence[_ForceInstall],
    created_directories: Sequence[tuple[tuple[str, ...], tuple[int, int]]],
) -> list[BaseException]:
    errors: list[BaseException] = []
    for install in reversed(installs):
        if install.installed_snapshot is None:
            continue
        try:
            current = authority.read_file_snapshot(install.target_parts)
            _require_same_snapshot(
                install.installed_snapshot,
                current,
                label=f"force rollback target {install.target_parts[-1]}",
            )
            moved = authority.guarded_move_entry(
                install.target_parts,
                install.stage_parts,
                guard=_snapshot_guard(
                    install.target_parent_identity,
                    install.installed_snapshot,
                    label=f"force rollback target {install.target_parts[-1]}",
                ),
                expected_target_parent_identity=transaction.root_identity,
            )
            _require_same_snapshot(
                install.installed_snapshot,
                moved,
                label=f"force rollback target {install.target_parts[-1]}",
            )
            transaction.add_file(install.stage_parts, moved)
            install.installed_snapshot = None
        except BaseException as rollback_error:
            errors.append(rollback_error)

    for install in reversed(installs):
        if install.backup_snapshot is None:
            continue
        try:
            restored = authority.guarded_move_entry(
                install.backup_parts,
                install.target_parts,
                guard=_snapshot_guard(
                    transaction.root_identity,
                    install.backup_snapshot,
                    label=f"force restore {install.target_parts[-1]}",
                ),
                expected_target_parent_identity=install.target_parent_identity,
            )
            _require_same_snapshot(
                install.backup_snapshot,
                restored,
                label=f"force restore {install.target_parts[-1]}",
            )
            transaction.discard_file(install.backup_parts)
            install.backup_snapshot = None
        except BaseException as rollback_error:
            errors.append(rollback_error)

    for parts, identity in reversed(created_directories):
        try:
            if not authority.remove_empty_directory(
                parts,
                expected_identity=identity,
            ):
                metadata = authority.entry_metadata(parts)
                if metadata is not None:
                    raise OSError("Scaffold rollback refused to remove a non-empty or " f"changed directory: {'/'.join(parts)}")
        except BaseException as rollback_error:
            errors.append(rollback_error)
    return errors


def _discard_force_backups(
    authority: _WindowsModuleAuthority,
    transaction: _OwnedTransaction,
    installs: Sequence[_ForceInstall],
) -> list[BaseException]:
    errors: list[BaseException] = []
    for install in installs:
        if install.backup_snapshot is None:
            continue
        try:
            authority.guarded_remove_file(
                install.backup_parts,
                guard=_snapshot_guard(
                    transaction.root_identity,
                    install.backup_snapshot,
                    label=f"force backup cleanup {install.target_parts[-1]}",
                ),
            )
            transaction.discard_file(install.backup_parts)
            install.backup_snapshot = None
        except BaseException as cleanup_error:
            errors.append(cleanup_error)
    return errors


def _cleanup_transaction_best_effort(
    authority: _WindowsModuleAuthority,
    transaction: _OwnedTransaction,
) -> None:
    errors: list[BaseException] = []
    try:
        if authority.entry_metadata(transaction.parts) is None:
            transaction.directories.clear()
            transaction.files.clear()
            return
    except BaseException as error:
        errors.append(error)
    try:
        if not errors:
            _require_owned_transaction(authority, transaction)
    except BaseException as error:
        errors.append(error)
    if not errors:
        for parts in sorted(
            transaction.files,
            key=lambda value: (len(value), value),
            reverse=True,
        ):
            snapshot = transaction.files[parts]
            parent_identity = transaction.directories.get(parts[:-1])
            if parent_identity is None:
                errors.append(OSError("Windows scaffold cleanup lost the retained parent " f"identity for {'/'.join(parts)}"))
                continue
            try:
                authority.guarded_remove_file(
                    parts,
                    guard=_snapshot_guard(
                        parent_identity,
                        snapshot,
                        label=f"transaction cleanup {'/'.join(parts)}",
                    ),
                )
                transaction.discard_file(parts)
            except BaseException as error:
                errors.append(error)
        for parts in sorted(
            transaction.directories,
            key=lambda value: (len(value), value),
            reverse=True,
        ):
            if parts not in transaction.directories:
                continue
            identity = transaction.directories[parts]
            try:
                removed = authority.remove_empty_directory(
                    parts,
                    expected_identity=identity,
                )
                if not removed and authority.entry_metadata(parts) is not None:
                    raise OSError("Windows scaffold cleanup refused to remove a " f"non-empty directory: {'/'.join(parts)}")
                transaction.directories.pop(parts, None)
            except BaseException as error:
                errors.append(error)
    if errors:
        logger.warning(
            "Windows scaffold transaction preserved for recovery at %s: %s",
            authority.path.joinpath(*transaction.parts),
            "; ".join(str(error) for error in errors),
        )


def _require_owned_transaction(
    authority: _WindowsModuleAuthority,
    transaction: _OwnedTransaction,
) -> None:
    for parts, expected_identity in transaction.directories.items():
        metadata = _require_directory(authority, parts)
        if metadata.identity != expected_identity:
            raise OSError("Windows scaffold transaction directory changed before " f"cleanup: {'/'.join(parts)}")
        actual_names = set(authority.directory_names(parts))
        expected_names = {path[len(parts)] for path in (*transaction.directories, *transaction.files) if len(path) > len(parts) and path[: len(parts)] == parts}
        if actual_names != expected_names:
            raise OSError(
                "Windows scaffold transaction contains unexpected recovery "
                f"data at {'/'.join(parts)} "
                f"(actual={sorted(actual_names)}, "
                f"expected={sorted(expected_names)})"
            )
    for parts, expected in transaction.files.items():
        current = authority.read_file_snapshot(parts)
        _require_same_snapshot(
            expected,
            current,
            label=f"transaction file {'/'.join(parts)}",
        )


def _prepared_batch(
    scaffolds: Sequence[tuple[str, str, str, Sequence[Mapping[str, object]]]],
) -> tuple[tuple[str, str, str, tuple[_RenderedFile, ...]], ...]:
    prepared: list[tuple[str, str, str, tuple[_RenderedFile, ...]]] = []
    seen_targets: set[tuple[str, str]] = set()
    seen_folders: set[tuple[str, str]] = set()
    for family, object_id, folder_name, rendered_files in scaffolds:
        family = _exact_component(family, label="module family")
        object_id = _exact_component(object_id, label="module object id")
        folder_name = _exact_component(folder_name, label="module folder")
        key = (
            portable_path_identity(family),
            portable_path_identity(object_id),
        )
        if key in seen_targets:
            raise OSError(f"Scaffold batch contains a portable module alias: {family}/{object_id}")
        seen_targets.add(key)
        folder_key = (
            portable_path_identity(family),
            portable_path_identity(folder_name),
        )
        if folder_key in seen_folders:
            raise OSError("Scaffold batch contains a duplicate portable module folder: " f"{family}/{folder_name}")
        seen_folders.add(folder_key)
        prepared.append(
            (
                family,
                object_id,
                folder_name,
                _rendered_files(rendered_files),
            )
        )
    return tuple(prepared)


def _preflight_new_targets(
    authority: _WindowsModuleAuthority,
    aliases: Sequence[tuple[tuple[str, ...], str, str]],
) -> None:
    for family_parts, object_id, folder_name in aliases:
        _require_exact_existing_directory_path(
            authority,
            family_parts,
            missing_ok=True,
        )
        _require_no_module_alias(
            authority,
            family_parts,
            object_id=object_id,
            allowed_names=(),
        )
        _require_missing_entry(
            authority,
            (*family_parts, folder_name),
            folder_name,
        )


def _require_no_module_alias(
    authority: _WindowsModuleAuthority,
    family_parts: tuple[str, ...],
    *,
    object_id: str,
    allowed_names: Sequence[str],
) -> None:
    names = _directory_names_if_present(authority, family_parts)
    logical_key = portable_path_identity(object_id)
    allowed = set(allowed_names)
    aliases = sorted(name for name in names if portable_path_identity(_module_folder_object_id(name)) == logical_key and name not in allowed)
    if aliases:
        raise OSError(f"Module {object_id!r} has a conflicting physical folder: " f"{', '.join(aliases)}.")


def _require_exact_directory_name(
    authority: _WindowsModuleAuthority,
    parent_parts: tuple[str, ...],
    name: str,
) -> None:
    names = authority.directory_names(parent_parts)
    if name not in names:
        aliases = [candidate for candidate in names if portable_path_identity(candidate) == portable_path_identity(name)]
        detail = f" (found {aliases[0]!r})" if aliases else ""
        raise OSError(f"Module directory spelling changed before mutation: {name!r}{detail}")


def _directory_names_if_present(
    authority: _WindowsModuleAuthority,
    parts: tuple[str, ...],
) -> tuple[str, ...]:
    metadata = authority.entry_metadata(parts)
    if metadata is None:
        return ()
    if not metadata.is_directory:
        raise OSError(f"Module source path is not a directory: {'/'.join(parts)}")
    return authority.directory_names(parts)


def _require_exact_existing_directory_path(
    authority: _WindowsModuleAuthority,
    parts: tuple[str, ...],
    *,
    missing_ok: bool,
) -> bool:
    for index in range(1, len(parts) + 1):
        current = parts[:index]
        metadata = authority.entry_metadata(current)
        if metadata is None:
            if missing_ok:
                return False
            raise FileNotFoundError(
                errno.ENOENT,
                f"Windows module directory does not exist: {'/'.join(current)}",
            )
        if not metadata.is_directory:
            raise OSError(f"Windows module path is not a directory: {'/'.join(current)}")
        _require_exact_directory_name(
            authority,
            current[:-1],
            current[-1],
        )
    return True


def _ensure_directory_chain(
    authority: _WindowsModuleAuthority,
    parts: tuple[str, ...],
) -> None:
    for index in range(1, len(parts) + 1):
        current = parts[:index]
        metadata, _created = authority.create_directory(
            current,
            exist_ok=True,
        )
        if not metadata.is_directory:
            raise OSError(f"Windows module path is not a directory: {'/'.join(current)}")
        _require_exact_directory_name(
            authority,
            current[:-1],
            current[-1],
        )


def _ensure_target_parent_directories(
    authority: _WindowsModuleAuthority,
    parts: tuple[str, ...],
    created: list[tuple[tuple[str, ...], tuple[int, int]]],
) -> None:
    for index in range(1, len(parts) + 1):
        current = parts[:index]
        metadata, was_created = authority.create_directory(
            current,
            exist_ok=True,
        )
        if not metadata.is_directory:
            raise OSError(f"Scaffold target parent is not a directory: {'/'.join(current)}")
        if was_created:
            created.append((current, metadata.identity))


def _rendered_files(
    rendered_files: Sequence[Mapping[str, object]],
) -> tuple[_RenderedFile, ...]:
    rendered: list[_RenderedFile] = []
    seen: set[str] = set()
    for item in rendered_files:
        relative_path = item.get("relative_module_path")
        content = item.get("content")
        if not isinstance(relative_path, str) or not isinstance(content, str):
            raise TypeError("Rendered scaffold files require string paths and content")
        parts = _exact_relative_parts(
            relative_path,
            label="rendered scaffold path",
        )
        key = portable_path_identity(PurePosixPath(*parts))
        if key in seen:
            raise OSError(f"Scaffold rendered duplicate portable target: {relative_path}")
        seen.add(key)
        rendered.append(
            _RenderedFile(
                parts=parts,
                payload=_normalized_scaffold_payload(content),
            )
        )
    return tuple(rendered)


def _exact_relative_parts(value: str, *, label: str) -> tuple[str, ...]:
    if "\\" in value:
        raise ValueError(f"{label} must use exact forward-slash components")
    path = PurePosixPath(value)
    parts = path.parts
    if not parts or path.is_absolute() or value != "/".join(parts):
        raise ValueError(f"{label} must be a normalized relative path: {value!r}")
    for component in parts:
        _exact_component(component, label=label)
    return parts


def _exact_component(value: str, *, label: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{label} must be a string")
    if PurePosixPath(value).parts != (value,) or "\\" in value:
        raise ValueError(f"{label} must be one exact path component: {value!r}")
    if unicodedata.normalize("NFC", value) != value:
        raise ValueError(f"{label} must use NFC spelling: {value!r}")
    if error := windows_portable_component_error(value):
        raise ValueError(f"{label} {value!r} is not portable to Windows because it {error}")
    return value


def _require_source_within_project(
    project_root: Path,
    source_root: Path,
) -> None:
    try:
        source_root.relative_to(project_root)
    except ValueError as error:
        raise OSError("Scaffold source root is outside the project root") from error


def _require_directory(
    authority: _WindowsModuleAuthority,
    parts: tuple[str, ...],
) -> Win32FileMetadata:
    metadata = authority.entry_metadata(parts)
    if metadata is None:
        raise FileNotFoundError(
            errno.ENOENT,
            f"Windows module directory does not exist: {'/'.join(parts)}",
        )
    if not metadata.is_directory:
        raise OSError(f"Windows module path is not a directory: {'/'.join(parts)}")
    return metadata


def _require_directory_identity(
    authority: _WindowsModuleAuthority,
    parts: tuple[str, ...],
    expected_identity: tuple[int, int],
    *,
    label: str,
) -> None:
    metadata = _require_directory(authority, parts)
    if metadata.identity != expected_identity:
        raise OSError(f"{label} changed during mutation")


def _require_missing_entry(
    authority: _WindowsModuleAuthority,
    parts: tuple[str, ...],
    name: str,
) -> None:
    if authority.entry_metadata(parts) is not None:
        raise FileExistsError(f"Module entry already exists: {name}")


def _require_missing_or_same_entry(
    authority: _WindowsModuleAuthority,
    parts: tuple[str, ...],
    source_metadata: Win32FileMetadata,
    name: str,
) -> None:
    target = authority.entry_metadata(parts)
    if target is None:
        return
    if target.identity == source_metadata.identity:
        return
    raise FileExistsError(f"Module entry already exists: {name}")


def _require_metadata_snapshot(
    metadata: Win32FileMetadata | None,
    snapshot: Win32FileSnapshot,
    *,
    label: str,
) -> None:
    if metadata is None or not _same_metadata_shape(
        metadata,
        snapshot.metadata,
    ):
        raise OSError(f"{label} changed while it was retained")


def _require_entry_snapshot(
    authority: _WindowsModuleAuthority,
    parts: tuple[str, ...],
    *,
    label: str,
) -> Win32FileSnapshot:
    snapshot = authority.read_file_snapshot(parts)
    if snapshot is None:
        raise FileNotFoundError(
            errno.ENOENT,
            f"{label} disappeared before mutation",
        )
    return snapshot


def _require_entry_snapshot_matches(
    authority: _WindowsModuleAuthority,
    parts: tuple[str, ...],
    expected: Win32FileSnapshot,
    *,
    label: str,
) -> None:
    current = authority.read_file_snapshot(parts)
    _require_same_snapshot(expected, current, label=label)


def _same_metadata_shape(
    left: Win32FileMetadata,
    right: Win32FileMetadata,
) -> bool:
    return left.identity == right.identity and left.attributes == right.attributes and left.size == right.size


def _snapshot_guard(
    expected_parent_identity: tuple[int, int],
    expected_snapshot: Win32FileSnapshot,
    *,
    label: str,
) -> Win32FileGuard:
    def guard(
        parent_identity: tuple[int, int],
        snapshot: Win32FileSnapshot | None,
    ) -> None:
        if parent_identity != expected_parent_identity:
            raise OSError(f"{label} parent changed before mutation")
        _require_same_snapshot(
            expected_snapshot,
            snapshot,
            label=label,
        )

    return guard


def _require_same_snapshot(
    expected: Win32FileSnapshot,
    current: Win32FileSnapshot | None,
    *,
    label: str,
) -> None:
    if current is None:
        raise FileNotFoundError(
            errno.ENOENT,
            f"{label} disappeared before mutation",
        )
    if current.metadata != expected.metadata:
        raise OSError(f"{label} identity or metadata changed before mutation")
    if current.content != expected.content:
        raise OSError(f"{label} content changed before mutation")


def _capture_tree(
    authority: _WindowsModuleAuthority,
    root_parts: tuple[str, ...],
) -> _TreeInventory:
    directories: dict[tuple[str, ...], Win32FileMetadata] = {}
    files: dict[tuple[str, ...], Win32FileSnapshot] = {}

    def visit(
        absolute_parts: tuple[str, ...],
        relative_parts: tuple[str, ...],
    ) -> None:
        before = _require_directory(authority, absolute_parts)
        names = authority.directory_names(absolute_parts)
        portable_names: set[str] = set()
        for name in names:
            _exact_component(name, label="retained module entry")
            key = portable_path_identity(name)
            if key in portable_names:
                raise OSError("Retained module directory contains a portable name " f"collision: {'/'.join((*relative_parts, name))}")
            portable_names.add(key)
            child_absolute = (*absolute_parts, name)
            child_relative = (*relative_parts, name)
            metadata = authority.entry_metadata(child_absolute)
            if metadata is None:
                raise OSError("Retained module entry disappeared while it was read: " f"{'/'.join(child_relative)}")
            if metadata.is_directory:
                visit(child_absolute, child_relative)
            else:
                snapshot = authority.read_file_snapshot(child_absolute)
                if snapshot is None or not _same_metadata_shape(
                    snapshot.metadata,
                    metadata,
                ):
                    raise OSError("Retained module file changed while it was read: " f"{'/'.join(child_relative)}")
                files[child_relative] = snapshot
        after = _require_directory(authority, absolute_parts)
        if before != after or names != authority.directory_names(absolute_parts):
            raise OSError("Retained module directory changed while it was read: " f"{'/'.join(relative_parts) or '.'}")
        directories[relative_parts] = after

    visit(root_parts, ())
    return _TreeInventory(directories=directories, files=files)


def _require_tree(
    authority: _WindowsModuleAuthority,
    root_parts: tuple[str, ...],
    expected: _TreeInventory,
) -> None:
    current = _capture_tree(authority, root_parts)
    if current.directories != expected.directories:
        raise OSError(f"Retained module directories changed: {'/'.join(root_parts)}")
    if current.files != expected.files:
        raise OSError(f"Retained module files changed: {'/'.join(root_parts)}")


def _remove_inventory_exact(
    authority: _WindowsModuleAuthority,
    root_parts: tuple[str, ...],
    inventory: _TreeInventory,
) -> None:
    """Delete only entries that still match one captured quarantine inventory."""

    _require_tree(authority, root_parts, inventory)
    for relative, snapshot in sorted(
        inventory.files.items(),
        key=lambda item: (len(item[0]), item[0]),
        reverse=True,
    ):
        parent = inventory.directories[relative[:-1]]
        authority.guarded_remove_file(
            (*root_parts, *relative),
            guard=_snapshot_guard(
                parent.identity,
                snapshot,
                label=f"module quarantine file {'/'.join(relative)}",
            ),
        )
    for relative, metadata in sorted(
        inventory.directories.items(),
        key=lambda item: (len(item[0]), item[0]),
        reverse=True,
    ):
        parts = (*root_parts, *relative)
        removed = authority.remove_empty_directory(
            parts,
            expected_identity=metadata.identity,
        )
        if not removed and authority.entry_metadata(parts) is not None:
            raise OSError("Module quarantine cleanup refused to remove a changed or " f"non-empty directory: {'/'.join(parts)}")


def _track_inventory(
    transaction: _OwnedTransaction,
    root_parts: tuple[str, ...],
    inventory: _TreeInventory,
) -> None:
    for relative, metadata in inventory.directories.items():
        transaction.directories[(*root_parts, *relative)] = metadata.identity
    for relative, snapshot in inventory.files.items():
        transaction.files[(*root_parts, *relative)] = snapshot


def _inventory_digest(inventory: _TreeInventory) -> str:
    digest = hashlib.sha256()
    entries: list[tuple[str, tuple[str, ...], Win32FileMetadata, str]] = []
    entries.extend(("d", path, metadata, "") for path, metadata in inventory.directories.items())
    entries.extend(
        (
            "f",
            path,
            snapshot.metadata,
            snapshot.content_sha256 or "",
        )
        for path, snapshot in inventory.files.items()
    )
    for kind, path, metadata, content_digest in sorted(
        entries,
        key=lambda item: (item[1], item[0]),
    ):
        encoded_path = "/".join(path).encode("utf-8")
        digest.update(kind.encode("ascii"))
        digest.update(len(encoded_path).to_bytes(8, "big"))
        digest.update(encoded_path)
        for value in (
            metadata.volume_serial,
            metadata.file_id,
            metadata.attributes,
            metadata.size,
            metadata.mtime_ns,
        ):
            encoded = str(value).encode("ascii")
            digest.update(len(encoded).to_bytes(4, "big"))
            digest.update(encoded)
        digest.update(content_digest.encode("ascii"))
    return digest.hexdigest()


def _quarantine_expectation(
    name: str,
) -> tuple[tuple[int, int], str]:
    match = _QUARANTINE_PATTERN.fullmatch(name)
    if match is None:
        raise ValueError("Module quarantine name does not carry a retained identity and " "content digest")
    return (
        (int(match.group(1), 16), int(match.group(2), 16)),
        match.group(3),
    )


def _raise_rollback_incomplete(
    transaction: _OwnedTransaction,
    errors: Sequence[BaseException],
    *,
    source_root: Path,
    cause: BaseException,
) -> None:
    recovery_path = source_root.joinpath(*transaction.parts)
    details = "; ".join(str(error) for error in errors)
    raise WindowsScaffoldRollbackIncomplete(
        details,
        recovery_path,
    ) from cause


def _module_folder_object_id(folder_name: str) -> str:
    return folder_name.split(" - ", 1)[0].strip()


def _normalized_scaffold_payload(content: str) -> bytes:
    normalized_content = content.rstrip("\n")
    return f"{normalized_content}\n".encode("utf-8")


def _is_at_or_below(
    path: tuple[str, ...],
    parent: tuple[str, ...],
) -> bool:
    return len(path) >= len(parent) and path[: len(parent)] == parent
