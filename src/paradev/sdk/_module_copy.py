"""Descriptor-anchored module tree duplication for SDK authoring."""

from __future__ import annotations

import errno
import hashlib
import json
import os
import stat
import unicodedata
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from uuid import uuid4

from paradev.build.authoring import ModuleIdentityContext, ModuleIdentityRewriter
from paradev.portable_paths import windows_portable_component_error

_DIRECTORY_FLAGS = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
_FILE_FLAGS = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_CLOEXEC", 0)
_CREATE_FILE_FLAGS = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
_TRANSACTION_ROOT = (".paradev", "module-transactions")
_SYSTEM_TREE = ".paradev"
_DURABLE_SYSTEM_FILES = frozenset({"meta.yaml"})
_ANCHORED_MODULE_COPY_SUPPORTED = (
    os.name != "nt"
    and os.open in os.supports_dir_fd
    and os.mkdir in os.supports_dir_fd
    and os.stat in os.supports_dir_fd
    and os.unlink in os.supports_dir_fd
    and os.rmdir in os.supports_dir_fd
    and os.rename in os.supports_dir_fd
    and os.link in os.supports_dir_fd
    and os.link in os.supports_follow_symlinks
    and os.listdir in os.supports_fd
    and os.stat in os.supports_follow_symlinks
    and hasattr(os, "O_DIRECTORY")
    and hasattr(os, "O_NOFOLLOW")
    and hasattr(os, "O_NONBLOCK")
)


class ModuleCopyUnavailable(OSError):
    """Raised when a host cannot guarantee safe module duplication."""


class ModuleCopySafetyError(OSError):
    """Raised when a module tree is unsafe to inspect or duplicate."""

    def __init__(self, code: str, message: str, *, path: Path | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.path = path


class ModuleCopyRollbackIncomplete(OSError):
    """Raised when failed-copy recovery data must remain on disk."""

    def __init__(self, message: str, recovery_path: Path) -> None:
        super().__init__(message)
        self.recovery_path = recovery_path


@dataclass(frozen=True, slots=True)
class ModuleCopyDirectory:
    """One stable source directory in a module-copy plan."""

    relative_path: str
    identity: tuple[int, int]
    mode: int
    mtime_ns: int

    def to_view(self) -> dict[str, object]:
        """Return a JSON-safe directory inventory row."""

        return {
            "relative_path": self.relative_path,
            "kind": "directory",
            "identity": list(self.identity),
            "mode": self.mode,
            "mtime_ns": str(self.mtime_ns),
            "action": "copy",
        }


@dataclass(frozen=True, slots=True)
class ModuleCopyFile:
    """One stable regular source file in a module-copy plan."""

    relative_path: str
    identity: tuple[int, int]
    mode: int
    mtime_ns: int
    size_bytes: int
    sha256: str

    def to_view(self) -> dict[str, object]:
        """Return a JSON-safe file inventory row."""

        return {
            "relative_path": self.relative_path,
            "kind": "file",
            "identity": list(self.identity),
            "mode": self.mode,
            "mtime_ns": str(self.mtime_ns),
            "size_bytes": self.size_bytes,
            "sha256": self.sha256,
            "action": "copy",
        }


@dataclass(frozen=True, slots=True)
class ModuleCopyTargetDirectory:
    """One projected target directory in a module-copy plan."""

    source_relative_path: str
    relative_path: str
    mode: int

    @property
    def action(self) -> str:
        """Return the reader-facing target operation."""

        return "copy" if self.source_relative_path == self.relative_path else "rename"


@dataclass(frozen=True, slots=True)
class ModuleCopyTargetFile:
    """One projected target file in a module-copy plan."""

    source_relative_path: str
    relative_path: str
    mode: int
    size_bytes: int
    sha256: str
    content_rewritten: bool

    @property
    def action(self) -> str:
        """Return the reader-facing target operation."""

        path_rewritten = self.source_relative_path != self.relative_path
        if path_rewritten and self.content_rewritten:
            return "rewrite_and_rename"
        if path_rewritten:
            return "rename"
        if self.content_rewritten:
            return "rewrite"
        return "copy"


@dataclass(frozen=True, slots=True)
class ModuleCopyExclusion:
    """One exact module-local system entry excluded from duplication."""

    relative_path: str
    kind: str
    identity: tuple[int, int]
    mode: int
    mtime_ns: int

    def to_view(self) -> dict[str, object]:
        """Return a JSON-safe exclusion row."""

        return {
            "relative_path": self.relative_path,
            "kind": self.kind,
            "identity": list(self.identity),
            "mode": self.mode,
            "mtime_ns": str(self.mtime_ns),
            "reason": "module_local_system_tree",
            "action": "exclude",
        }


@dataclass(frozen=True, slots=True)
class ModuleCopySnapshot:
    """Stable source inventory and destination precondition for one copy."""

    source_root_identity: tuple[int, int]
    source_modules_identity: tuple[int, int]
    source_family_identity: tuple[int, int]
    source_module_identity: tuple[int, int]
    destination_root_identity: tuple[int, int]
    destination_modules_identity: tuple[int, int] | None
    destination_family_identity: tuple[int, int] | None
    destination_entry_count: int
    destination_entry_names_digest: str
    directories: tuple[ModuleCopyDirectory, ...]
    files: tuple[ModuleCopyFile, ...]
    target_directories: tuple[ModuleCopyTargetDirectory, ...]
    target_files: tuple[ModuleCopyTargetFile, ...]
    exclusions: tuple[ModuleCopyExclusion, ...]
    tree_digest: str
    content_digest: str
    target_content_digest: str
    identity_rewriter: str | None

    @property
    def size_bytes(self) -> int:
        """Return the total regular-file byte count."""

        return sum(item.size_bytes for item in self.files)

    @property
    def target_size_bytes(self) -> int:
        """Return the total projected target-file byte count."""

        return sum(item.size_bytes for item in self.target_files)

    @property
    def rewritten_file_count(self) -> int:
        """Return the number of files whose bytes change."""

        return sum(item.content_rewritten for item in self.target_files)

    @property
    def renamed_path_count(self) -> int:
        """Return the number of projected entries whose paths change."""

        return sum(item.source_relative_path != item.relative_path for item in (*self.target_directories, *self.target_files))

    def directory_views(self) -> list[dict[str, object]]:
        """Return source directories with their projected target paths."""

        targets = {item.source_relative_path: item for item in self.target_directories}
        return [
            {
                **item.to_view(),
                "target_relative_path": targets[item.relative_path].relative_path,
                "action": targets[item.relative_path].action,
            }
            for item in self.directories
        ]

    def file_views(self) -> list[dict[str, object]]:
        """Return source files with their projected target fingerprints."""

        targets = {item.source_relative_path: item for item in self.target_files}
        return [
            {
                **item.to_view(),
                "target_relative_path": targets[item.relative_path].relative_path,
                "target_size_bytes": targets[item.relative_path].size_bytes,
                "target_sha256": targets[item.relative_path].sha256,
                "content_rewritten": targets[item.relative_path].content_rewritten,
                "action": targets[item.relative_path].action,
            }
            for item in self.files
        ]

    def source_view(self) -> dict[str, object]:
        """Return source identities and inventory digests."""

        return {
            "root_identity": list(self.source_root_identity),
            "modules_identity": list(self.source_modules_identity),
            "family_identity": list(self.source_family_identity),
            "module_identity": list(self.source_module_identity),
            "tree_digest": self.tree_digest,
            "content_digest": self.content_digest,
            "identity_rewriter": self.identity_rewriter,
        }

    def destination_view(
        self,
        *,
        target_identity: tuple[int, int] | None = None,
    ) -> dict[str, object]:
        """Return destination identities and target-absence preconditions."""

        return {
            "root_identity": list(self.destination_root_identity),
            "modules_identity": (list(self.destination_modules_identity) if self.destination_modules_identity is not None else None),
            "family_identity": (list(self.destination_family_identity) if self.destination_family_identity is not None else None),
            "target_identity": (list(target_identity) if target_identity is not None else None),
            "entry_count": self.destination_entry_count,
            "entry_names_digest": self.destination_entry_names_digest,
            "content_digest": self.target_content_digest,
        }


@dataclass(frozen=True, slots=True)
class ModuleCopyInstall:
    """Identity of one successfully installed duplicate module."""

    target_identity: tuple[int, int]
    cleanup_path: Path | None = None


@dataclass(frozen=True, slots=True)
class _RootAuthority:
    """Retained no-follow authority for one configured source root."""

    requested_path: Path
    path: Path
    descriptor: int
    identity: tuple[int, int]

    def close(self) -> None:
        """Close the retained root descriptor."""

        _close(self.descriptor)

    def verify_path(self) -> None:
        """Reject a configured root replaced after it was opened."""

        current = _open_root(self.path, label="configured source root")
        try:
            if current.identity != self.identity:
                raise ModuleCopySafetyError(
                    "concurrent_change",
                    f"Configured source root changed during module duplication: {self.requested_path}.",
                    path=self.requested_path,
                )
        finally:
            current.close()


@dataclass(frozen=True, slots=True)
class _Tree:
    """Captured module tree plus its retained root metadata."""

    directories: tuple[ModuleCopyDirectory, ...]
    files: tuple[ModuleCopyFile, ...]
    exclusions: tuple[ModuleCopyExclusion, ...]
    tree_digest: str
    content_digest: str


@dataclass(frozen=True, slots=True)
class _TargetTree:
    """Deterministic target projection produced by a family rewriter."""

    directories: tuple[ModuleCopyTargetDirectory, ...]
    files: tuple[ModuleCopyTargetFile, ...]
    content_digest: str


@dataclass(frozen=True, slots=True)
class _Destination:
    """Captured destination family precondition."""

    modules_identity: tuple[int, int] | None
    family_identity: tuple[int, int] | None
    entry_count: int
    entry_names_digest: str


@dataclass(frozen=True, slots=True)
class _StageFile:
    """One flat staged file retained by transaction identity."""

    name: str
    identity: tuple[int, int]
    size_bytes: int
    sha256: str


def inspect_module_copy(
    source_root: Path,
    destination_source_root: Path,
    *,
    family: str,
    source_object_id: str,
    source_name: str,
    target_name: str,
    target_object_id: str,
    identity_rewriter: ModuleIdentityRewriter | None = None,
) -> ModuleCopySnapshot:
    """Inspect one module tree and its create-only duplicate destination."""

    _require_supported()
    family = _component(family, label="module family")
    source_object_id = _component(
        source_object_id,
        label="source module object id",
    )
    source_name = _component(source_name, label="source module folder")
    target_name = _component(target_name, label="target module folder")
    target_object_id = _component(
        target_object_id,
        label="target module object id",
    )
    source = _open_root(source_root, label="source root")
    destination: _RootAuthority | None = None
    source_modules_fd: int | None = None
    source_family_fd: int | None = None
    source_module_fd: int | None = None
    try:
        destination = _open_root(
            destination_source_root,
            label="destination source root",
        )
        source_modules_fd = _open_required_directory(
            source.descriptor,
            "modules",
            source.path / "modules",
            code="source_path_unsafe",
        )
        source_family_fd = _open_required_directory(
            source_modules_fd,
            family,
            source.path / "modules" / family,
            code="source_path_unsafe",
        )
        source_module_fd = _open_required_directory(
            source_family_fd,
            source_name,
            source.path / "modules" / family / source_name,
            code="source_path_unsafe",
        )
        _require_same_device(
            source.identity[0],
            os.fstat(source_modules_fd),
            source.path / "modules",
        )
        _require_same_device(
            source.identity[0],
            os.fstat(source_family_fd),
            source.path / "modules" / family,
        )
        source_module_stat = os.fstat(source_module_fd)
        _require_same_device(
            source.identity[0],
            source_module_stat,
            source.path / "modules" / family / source_name,
        )
        tree = _capture_tree(
            source_module_fd,
            source.path / "modules" / family / source_name,
            root_device=source.identity[0],
        )
        target_tree = _project_target_tree(
            source_module_fd,
            source.path / "modules" / family / source_name,
            tree,
            context=ModuleIdentityContext(
                family=family,
                source_object_id=source_object_id,
                target_object_id=target_object_id,
            ),
            identity_rewriter=identity_rewriter,
        )
        destination_state = _capture_destination(
            destination,
            family=family,
            target_name=target_name,
            target_object_id=target_object_id,
        )
        _require_source_path_identity(
            source,
            family=family,
            source_name=source_name,
            modules_identity=_identity(os.fstat(source_modules_fd)),
            family_identity=_identity(os.fstat(source_family_fd)),
            module_identity=_identity(source_module_stat),
        )
        if (
            _capture_destination(
                destination,
                family=family,
                target_name=target_name,
                target_object_id=target_object_id,
            )
            != destination_state
        ):
            raise ModuleCopySafetyError(
                "concurrent_change",
                "Module-copy destination changed during planning.",
                path=destination.path / "modules" / family / target_name,
            )
        source.verify_path()
        destination.verify_path()
        return ModuleCopySnapshot(
            source_root_identity=source.identity,
            source_modules_identity=_identity(os.fstat(source_modules_fd)),
            source_family_identity=_identity(os.fstat(source_family_fd)),
            source_module_identity=_identity(source_module_stat),
            destination_root_identity=destination.identity,
            destination_modules_identity=destination_state.modules_identity,
            destination_family_identity=destination_state.family_identity,
            destination_entry_count=destination_state.entry_count,
            destination_entry_names_digest=destination_state.entry_names_digest,
            directories=tree.directories,
            files=tree.files,
            target_directories=target_tree.directories,
            target_files=target_tree.files,
            exclusions=tree.exclusions,
            tree_digest=tree.tree_digest,
            content_digest=tree.content_digest,
            target_content_digest=target_tree.content_digest,
            identity_rewriter=(str(identity_rewriter.identifier) if identity_rewriter is not None else None),
        )
    finally:
        for descriptor in (
            source_module_fd,
            source_family_fd,
            source_modules_fd,
        ):
            if descriptor is not None:
                _close(descriptor)
        if destination is not None:
            destination.close()
        source.close()


def install_module_copy(
    source_root: Path,
    destination_source_root: Path,
    *,
    family: str,
    source_object_id: str,
    source_name: str,
    target_name: str,
    target_object_id: str,
    expected: ModuleCopySnapshot,
    identity_rewriter: ModuleIdentityRewriter | None = None,
) -> ModuleCopyInstall:
    """Install one exact module-copy plan without overwriting a target."""

    current = inspect_module_copy(
        source_root,
        destination_source_root,
        family=family,
        source_object_id=source_object_id,
        source_name=source_name,
        target_name=target_name,
        target_object_id=target_object_id,
        identity_rewriter=identity_rewriter,
    )
    if current != expected:
        raise OSError(
            errno.EAGAIN,
            "Module copy source or destination changed after planning.",
        )

    source = _open_root(source_root, label="source root")
    destination = _open_root(
        destination_source_root,
        label="destination source root",
    )
    descriptors: list[int] = []
    transaction_name = f"duplicate-{uuid4().hex}.txn"
    transaction_path = destination.path.joinpath(*_TRANSACTION_ROOT) / transaction_name
    transaction_fd: int | None = None
    transactions_fd: int | None = None
    transaction_identity: tuple[int, int] | None = None
    family_fd: int | None = None
    source_module_fd: int | None = None
    target_identity: tuple[int, int] | None = None
    target_directory_identities: dict[str, tuple[int, int]] = {}
    staged: list[_StageFile] = []
    preserve_transaction = False
    identity_context = ModuleIdentityContext(
        family=family,
        source_object_id=source_object_id,
        target_object_id=target_object_id,
    )
    try:
        if source.identity != expected.source_root_identity:
            raise OSError(errno.EAGAIN, "Module copy source root identity changed.")
        if destination.identity != expected.destination_root_identity:
            raise OSError(
                errno.EAGAIN,
                "Module copy destination root identity changed.",
            )
        source_modules_fd = _open_required_directory(
            source.descriptor,
            "modules",
            source.path / "modules",
            code="concurrent_change",
        )
        descriptors.append(source_modules_fd)
        source_family_fd = _open_required_directory(
            source_modules_fd,
            family,
            source.path / "modules" / family,
            code="concurrent_change",
        )
        descriptors.append(source_family_fd)
        source_module_fd = _open_required_directory(
            source_family_fd,
            source_name,
            source.path / "modules" / family / source_name,
            code="concurrent_change",
        )
        descriptors.append(source_module_fd)
        if (
            _identity(os.fstat(source_modules_fd)) != expected.source_modules_identity
            or _identity(os.fstat(source_family_fd)) != expected.source_family_identity
            or _identity(os.fstat(source_module_fd)) != expected.source_module_identity
        ):
            raise OSError(errno.EAGAIN, "Module copy source path identity changed.")

        metadata_fd = _open_or_create_directory(
            destination.descriptor,
            _SYSTEM_TREE,
            mode=0o700,
            path=destination.path / _SYSTEM_TREE,
        )
        _require_same_device(
            destination.identity[0],
            os.fstat(metadata_fd),
            destination.path / _SYSTEM_TREE,
        )
        descriptors.append(metadata_fd)
        transactions_fd = _open_or_create_directory(
            metadata_fd,
            "module-transactions",
            mode=0o700,
            path=destination.path.joinpath(*_TRANSACTION_ROOT),
        )
        _require_same_device(
            destination.identity[0],
            os.fstat(transactions_fd),
            destination.path.joinpath(*_TRANSACTION_ROOT),
        )
        os.mkdir(transaction_name, 0o700, dir_fd=transactions_fd)
        transaction_fd = _open_required_directory(
            transactions_fd,
            transaction_name,
            transaction_path,
            code="concurrent_change",
        )
        transaction_identity = _identity(os.fstat(transaction_fd))
        _require_same_device(
            destination.identity[0],
            os.fstat(transaction_fd),
            transaction_path,
        )

        for index, (item, target) in enumerate(zip(expected.files, expected.target_files, strict=True)):
            stage_name = f"{index:08d}.stage"
            staged.append(
                _stage_source_file(
                    source_module_fd,
                    transaction_fd,
                    item,
                    target=target,
                    context=identity_context,
                    identity_rewriter=identity_rewriter,
                    stage_name=stage_name,
                    source_path=source.path / "modules" / family / source_name,
                )
            )

        source_tree = _capture_tree(
            source_module_fd,
            source.path / "modules" / family / source_name,
            root_device=source.identity[0],
        )
        if not _tree_matches_snapshot(source_tree, expected):
            raise OSError(errno.EAGAIN, "Module source changed while its files were staged.")
        _require_source_path_identity(
            source,
            family=family,
            source_name=source_name,
            modules_identity=expected.source_modules_identity,
            family_identity=expected.source_family_identity,
            module_identity=expected.source_module_identity,
        )

        modules_fd = _open_or_create_directory(
            destination.descriptor,
            "modules",
            mode=0o755,
            path=destination.path / "modules",
        )
        _require_same_device(
            destination.identity[0],
            os.fstat(modules_fd),
            destination.path / "modules",
        )
        descriptors.append(modules_fd)
        family_fd = _open_or_create_directory(
            modules_fd,
            family,
            mode=0o755,
            path=destination.path / "modules" / family,
        )
        _require_same_device(
            destination.identity[0],
            os.fstat(family_fd),
            destination.path / "modules" / family,
        )
        descriptors.append(family_fd)
        _require_destination_precondition(
            destination,
            modules_fd,
            family_fd,
            expected,
            target_name=target_name,
            target_object_id=target_object_id,
        )
        os.mkdir(
            target_name,
            _target_directory_mode(expected.target_directories, "."),
            dir_fd=family_fd,
        )
        created_target = os.stat(
            target_name,
            dir_fd=family_fd,
            follow_symlinks=False,
        )
        if not stat.S_ISDIR(created_target.st_mode):
            raise OSError(
                errno.EAGAIN,
                "Duplicated module target changed immediately after creation.",
            )
        target_identity = _identity(created_target)
        target_directory_identities["."] = target_identity
        target_fd = _open_required_directory(
            family_fd,
            target_name,
            destination.path / "modules" / family / target_name,
            code="concurrent_change",
        )
        descriptors.append(target_fd)
        os.fchmod(target_fd, _target_directory_mode(expected.target_directories, "."))
        if _identity(os.fstat(target_fd)) != target_identity:
            raise OSError(
                errno.EAGAIN,
                "Duplicated module target identity changed while opening it.",
            )

        target_directories: dict[str, int] = {".": target_fd}
        for item in expected.target_directories:
            if item.relative_path == ".":
                continue
            parent_path, name = _parent_and_name(item.relative_path)
            parent_fd = target_directories[parent_path]
            os.mkdir(name, item.mode, dir_fd=parent_fd)
            child_fd = _open_required_directory(
                parent_fd,
                name,
                destination.path / "modules" / family / target_name / PurePosixPath(item.relative_path),
                code="concurrent_change",
            )
            os.fchmod(child_fd, item.mode)
            target_directories[item.relative_path] = child_fd
            target_directory_identities[item.relative_path] = _identity(os.fstat(child_fd))
            descriptors.append(child_fd)

        for item, stage in zip(expected.target_files, staged, strict=True):
            parent_path, name = _parent_and_name(item.relative_path)
            _link_stage_file(
                transaction_fd,
                stage.name,
                target_directories[parent_path],
                name,
            )
            _require_file_fingerprint(
                target_directories[parent_path],
                name,
                expected=stage,
                label=f"duplicated module file {item.relative_path}",
            )
        for descriptor in target_directories.values():
            os.fsync(descriptor)
        os.fsync(family_fd)

        source_tree = _capture_tree(
            source_module_fd,
            source.path / "modules" / family / source_name,
            root_device=source.identity[0],
        )
        if not _tree_matches_snapshot(source_tree, expected):
            raise OSError(errno.EAGAIN, "Module source changed before duplicate commit.")
        target_tree = _capture_tree(
            target_fd,
            destination.path / "modules" / family / target_name,
            root_device=destination.identity[0],
        )
        if not _target_matches_install(
            target_tree,
            expected,
            staged,
            target_directory_identities,
        ):
            raise OSError(errno.EAGAIN, "Duplicated module contents changed during commit.")
        _require_target_alias_state(
            family_fd,
            target_name=target_name,
            target_object_id=target_object_id,
        )
        _require_source_path_identity(
            source,
            family=family,
            source_name=source_name,
            modules_identity=expected.source_modules_identity,
            family_identity=expected.source_family_identity,
            module_identity=expected.source_module_identity,
        )
        _require_destination_target_path(
            destination,
            family=family,
            target_name=target_name,
            family_identity=_identity(os.fstat(family_fd)),
            target_identity=target_identity,
        )
        source.verify_path()
        destination.verify_path()
        final_target_tree = _capture_tree(
            target_fd,
            destination.path / "modules" / family / target_name,
            root_device=destination.identity[0],
        )
        if not _target_matches_install(
            final_target_tree,
            expected,
            staged,
            target_directory_identities,
        ):
            raise OSError(
                errno.EAGAIN,
                "Duplicated module contents changed before commit completed.",
            )
        _cleanup_stage_files(transaction_fd, staged)
        os.fsync(transaction_fd)
        staged.clear()
    except BaseException as error:
        rollback_errors: list[BaseException] = []
        if family_fd is not None and transaction_fd is not None and target_identity is not None:
            try:
                _rollback_target(
                    family_fd,
                    target_name,
                    target_identity,
                    transaction_fd,
                    transaction_path=transaction_path,
                    expected=expected,
                    staged=staged,
                    directory_identities=target_directory_identities,
                    root_device=destination.identity[0],
                )
            except BaseException as rollback_error:
                rollback_errors.append(rollback_error)
        if transaction_fd is not None and staged:
            try:
                _cleanup_stage_files(transaction_fd, staged)
                staged.clear()
            except BaseException as cleanup_error:
                rollback_errors.append(cleanup_error)
        if rollback_errors:
            preserve_transaction = True
            details = "; ".join(str(item) for item in rollback_errors)
            raise ModuleCopyRollbackIncomplete(
                f"Module duplication rollback was incomplete: {details}",
                transaction_path,
            ) from error
        raise
    finally:
        for descriptor in reversed(descriptors):
            _close(descriptor)
        if transaction_fd is not None:
            _close(transaction_fd)
        if transactions_fd is not None and transaction_identity is not None and not preserve_transaction:
            try:
                _remove_transaction(
                    transactions_fd,
                    transaction_name,
                    transaction_identity,
                )
            except FileNotFoundError:
                pass
            except BaseException:
                preserve_transaction = True
        if transactions_fd is not None:
            _close(transactions_fd)
        destination.close()
        source.close()
    if target_identity is None:
        raise AssertionError("Successful module duplication lost its target identity.")
    if preserve_transaction:
        return ModuleCopyInstall(
            target_identity=target_identity,
            cleanup_path=transaction_path,
        )
    return ModuleCopyInstall(target_identity=target_identity)


def _require_supported() -> None:
    if not _ANCHORED_MODULE_COPY_SUPPORTED:
        raise ModuleCopyUnavailable("Safe descriptor-anchored module duplication is unavailable on this platform.")


def _component(value: str, *, label: str) -> str:
    normalized = unicodedata.normalize("NFC", value)
    if value != normalized:
        raise ModuleCopySafetyError(
            "nonportable_name",
            f"{label.capitalize()} must use NFC-normalized spelling: {value!r}.",
        )
    if value in {"", ".", ".."} or "/" in value or "\\" in value or value != value.strip():
        raise ModuleCopySafetyError(
            "nonportable_name",
            f"{label.capitalize()} must be one exact path component: {value!r}.",
        )
    if error := windows_portable_component_error(value):
        raise ModuleCopySafetyError(
            "nonportable_name",
            f"{label.capitalize()} is not portable to Windows because it {error}: {value!r}.",
        )
    if len(os.fsencode(value)) > 255:
        raise ModuleCopySafetyError(
            "nonportable_name",
            f"{label.capitalize()} exceeds the portable 255-byte filename limit: {value!r}.",
        )
    return value


def _open_root(path: Path, *, label: str) -> _RootAuthority:
    _require_supported()
    requested = path.expanduser()
    absolute = Path(os.path.abspath(requested))
    descriptor: int | None = None
    try:
        descriptor = os.open(absolute.anchor, _DIRECTORY_FLAGS)
        for index, part in enumerate(absolute.parts[1:], start=1):
            child = _open_required_directory(
                descriptor,
                part,
                Path(absolute.anchor).joinpath(*absolute.parts[1 : index + 1]),
                code="path_component_unsafe",
            )
            _close(descriptor)
            descriptor = child
        metadata = os.fstat(descriptor)
        return _RootAuthority(
            requested_path=requested,
            path=absolute,
            descriptor=descriptor,
            identity=_identity(metadata),
        )
    except ModuleCopySafetyError:
        if descriptor is not None:
            _close(descriptor)
        raise
    except OSError as error:
        if descriptor is not None:
            _close(descriptor)
        raise ModuleCopySafetyError(
            "path_unreadable",
            f"{label.capitalize()} cannot be opened without following links: {requested}.",
            path=requested,
        ) from error


def _open_required_directory(
    parent_fd: int,
    name: str,
    path: Path,
    *,
    code: str,
) -> int:
    names = os.listdir(parent_fd)
    if name not in names:
        aliases = [item for item in names if _portable_key(item) == _portable_key(name)]
        if aliases:
            raise ModuleCopySafetyError(
                "portable_collision",
                f"Path component {name!r} collides with {', '.join(sorted(aliases))!r}.",
                path=path,
            )
        raise ModuleCopySafetyError(
            code,
            f"Required module-copy directory does not exist: {path}.",
            path=path,
        )
    try:
        metadata = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except OSError as error:
        raise ModuleCopySafetyError(
            code,
            f"Module-copy directory cannot be inspected safely: {path}.",
            path=path,
        ) from error
    if stat.S_ISLNK(metadata.st_mode):
        raise ModuleCopySafetyError(
            "symlink",
            f"Module duplication refuses symbolic links: {path}.",
            path=path,
        )
    if not stat.S_ISDIR(metadata.st_mode):
        raise ModuleCopySafetyError(
            "special_entry",
            f"Module-copy path is not a directory: {path}.",
            path=path,
        )
    try:
        descriptor = os.open(name, _DIRECTORY_FLAGS, dir_fd=parent_fd)
    except OSError as error:
        raise ModuleCopySafetyError(
            code,
            f"Module-copy directory changed or crosses a link: {path}.",
            path=path,
        ) from error
    opened = os.fstat(descriptor)
    if _identity(opened) != _identity(metadata):
        _close(descriptor)
        raise ModuleCopySafetyError(
            "concurrent_change",
            f"Module-copy directory changed while it was opened: {path}.",
            path=path,
        )
    return descriptor


def _open_optional_directory(
    parent_fd: int,
    name: str,
    path: Path,
) -> int | None:
    names = os.listdir(parent_fd)
    if name not in names:
        aliases = [item for item in names if _portable_key(item) == _portable_key(name)]
        if aliases:
            raise ModuleCopySafetyError(
                "portable_collision",
                f"Path component {name!r} collides with {', '.join(sorted(aliases))!r}.",
                path=path,
            )
        return None
    return _open_required_directory(
        parent_fd,
        name,
        path,
        code="destination_path_unsafe",
    )


def _open_or_create_directory(
    parent_fd: int,
    name: str,
    *,
    mode: int,
    path: Path,
) -> int:
    descriptor = _open_optional_directory(parent_fd, name, path)
    if descriptor is not None:
        return descriptor
    try:
        os.mkdir(name, mode, dir_fd=parent_fd)
    except FileExistsError as error:
        raise OSError(
            errno.EAGAIN,
            f"Module-copy directory appeared concurrently: {path}.",
        ) from error
    return _open_required_directory(
        parent_fd,
        name,
        path,
        code="concurrent_change",
    )


def _capture_tree(
    root_fd: int,
    root_path: Path,
    *,
    root_device: int,
) -> _Tree:
    directories: list[ModuleCopyDirectory] = []
    files: list[ModuleCopyFile] = []
    exclusions: list[ModuleCopyExclusion] = []
    _capture_directory(
        root_fd,
        root_path,
        PurePosixPath(),
        root_device=root_device,
        directories=directories,
        files=files,
        exclusions=exclusions,
    )
    directory_rows = tuple(sorted(directories, key=lambda item: (item.relative_path.count("/"), item.relative_path)))
    file_rows = tuple(sorted(files, key=lambda item: item.relative_path))
    exclusion_rows = tuple(sorted(exclusions, key=lambda item: item.relative_path))
    full_view = {
        "directories": [item.to_view() for item in directory_rows],
        "files": [item.to_view() for item in file_rows],
        "exclusions": [item.to_view() for item in exclusion_rows],
    }
    content_view = {
        "directories": [
            {
                "relative_path": item.relative_path,
                "kind": "directory",
                "mode": item.mode,
            }
            for item in directory_rows
        ],
        "files": [
            {
                "relative_path": item.relative_path,
                "kind": "file",
                "mode": item.mode,
                "size_bytes": item.size_bytes,
                "sha256": item.sha256,
            }
            for item in file_rows
        ],
    }
    return _Tree(
        directories=directory_rows,
        files=file_rows,
        exclusions=exclusion_rows,
        tree_digest=_digest_json(full_view),
        content_digest=_digest_json(content_view),
    )


def _project_target_tree(
    source_module_fd: int,
    source_path: Path,
    tree: _Tree,
    *,
    context: ModuleIdentityContext,
    identity_rewriter: ModuleIdentityRewriter | None,
) -> _TargetTree:
    directories = tuple(
        sorted(
            (
                ModuleCopyTargetDirectory(
                    source_relative_path=item.relative_path,
                    relative_path=_target_relative_path(
                        item.relative_path,
                        source_path=source_path,
                        context=context,
                        identity_rewriter=identity_rewriter,
                        directory=True,
                    ),
                    mode=item.mode,
                )
                for item in tree.directories
            ),
            key=lambda item: (
                item.relative_path.count("/"),
                item.relative_path,
            ),
        )
    )
    files: list[ModuleCopyTargetFile] = []
    for item in tree.files:
        target_path = _target_relative_path(
            item.relative_path,
            source_path=source_path,
            context=context,
            identity_rewriter=identity_rewriter,
            directory=False,
        )
        target_content = _target_file_content(
            source_module_fd,
            source_path,
            item,
            context=context,
            identity_rewriter=identity_rewriter,
        )
        if target_content is None:
            target_size = item.size_bytes
            target_sha256 = item.sha256
            content_rewritten = False
        else:
            target_size = len(target_content)
            target_sha256 = hashlib.sha256(target_content).hexdigest()
            content_rewritten = target_size != item.size_bytes or target_sha256 != item.sha256
        files.append(
            ModuleCopyTargetFile(
                source_relative_path=item.relative_path,
                relative_path=target_path,
                mode=item.mode,
                size_bytes=target_size,
                sha256=target_sha256,
                content_rewritten=content_rewritten,
            )
        )
    target_files = tuple(sorted(files, key=lambda item: item.source_relative_path))
    _validate_target_tree(directories, target_files, source_path)
    content_view = {
        "directories": [
            {
                "relative_path": item.relative_path,
                "kind": "directory",
                "mode": item.mode,
            }
            for item in directories
        ],
        "files": [
            {
                "relative_path": item.relative_path,
                "kind": "file",
                "mode": item.mode,
                "size_bytes": item.size_bytes,
                "sha256": item.sha256,
            }
            for item in sorted(target_files, key=lambda item: item.relative_path)
        ],
    }
    return _TargetTree(
        directories=directories,
        files=target_files,
        content_digest=_digest_json(content_view),
    )


def _target_relative_path(
    relative_path: str,
    *,
    source_path: Path,
    context: ModuleIdentityContext,
    identity_rewriter: ModuleIdentityRewriter | None,
    directory: bool,
) -> str:
    if identity_rewriter is None:
        candidate = relative_path
    else:
        try:
            candidate = identity_rewriter.rewrite_path(context, relative_path)
        except Exception as error:
            raise ModuleCopySafetyError(
                "identity_rewrite",
                f"Module identity rewriter {identity_rewriter.identifier!r} " f"failed for path {relative_path!r}: {error}.",
                path=source_path / PurePosixPath(relative_path),
            ) from error
    if not isinstance(candidate, str):
        raise ModuleCopySafetyError(
            "identity_rewrite",
            f"Module identity rewriter returned a non-string path for {relative_path!r}.",
            path=source_path / PurePosixPath(relative_path),
        )
    if directory and relative_path == ".":
        if candidate != ".":
            raise ModuleCopySafetyError(
                "identity_rewrite",
                "Module identity rewriter must preserve the module root path '.'.",
                path=source_path,
            )
        return candidate
    normalized = unicodedata.normalize("NFC", candidate)
    projected = PurePosixPath(candidate)
    if (
        candidate != normalized
        or candidate != projected.as_posix()
        or projected.is_absolute()
        or not projected.parts
        or "." in projected.parts
        or ".." in projected.parts
        or "\\" in candidate
    ):
        raise ModuleCopySafetyError(
            "identity_rewrite",
            f"Module identity rewriter returned an unsafe target path for " f"{relative_path!r}: {candidate!r}.",
            path=source_path / PurePosixPath(relative_path),
        )
    for part in projected.parts:
        _component(part, label="rewritten module path component")
    return candidate


def _target_file_content(
    source_module_fd: int,
    source_path: Path,
    item: ModuleCopyFile,
    *,
    context: ModuleIdentityContext,
    identity_rewriter: ModuleIdentityRewriter | None,
) -> bytes | None:
    if identity_rewriter is None:
        return None
    try:
        rewrites = identity_rewriter.rewrites_content(
            context,
            item.relative_path,
        )
    except Exception as error:
        raise ModuleCopySafetyError(
            "identity_rewrite",
            f"Module identity rewriter {identity_rewriter.identifier!r} could " f"not classify {item.relative_path!r}: {error}.",
            path=source_path / PurePosixPath(item.relative_path),
        ) from error
    if type(rewrites) is not bool:
        raise ModuleCopySafetyError(
            "identity_rewrite",
            f"Module identity rewriter must return a boolean when classifying " f"{item.relative_path!r}.",
            path=source_path / PurePosixPath(item.relative_path),
        )
    if not rewrites:
        return None
    content = _read_source_file(source_module_fd, source_path, item)
    try:
        rewritten = identity_rewriter.rewrite_content(
            context,
            item.relative_path,
            content,
        )
    except Exception as error:
        raise ModuleCopySafetyError(
            "identity_rewrite",
            f"Module identity rewriter {identity_rewriter.identifier!r} failed " f"for {item.relative_path!r}: {error}.",
            path=source_path / PurePosixPath(item.relative_path),
        ) from error
    if not isinstance(rewritten, bytes):
        raise ModuleCopySafetyError(
            "identity_rewrite",
            f"Module identity rewriter returned non-byte content for " f"{item.relative_path!r}.",
            path=source_path / PurePosixPath(item.relative_path),
        )
    return rewritten


def _validate_target_tree(
    directories: tuple[ModuleCopyTargetDirectory, ...],
    files: tuple[ModuleCopyTargetFile, ...],
    source_path: Path,
) -> None:
    identities: dict[str, str] = {}
    directory_paths = {item.relative_path for item in directories}
    if "." not in directory_paths:
        raise ModuleCopySafetyError(
            "identity_rewrite",
            "Module identity rewrite omitted the target root directory.",
            path=source_path,
        )
    for path in (
        *(item.relative_path for item in directories if item.relative_path != "."),
        *(item.relative_path for item in files),
    ):
        key = _portable_relative_key(path)
        previous = identities.get(key)
        if previous is not None:
            raise ModuleCopySafetyError(
                "identity_rewrite_collision",
                f"Module identity rewrite maps multiple entries to the same " f"portable target path: {previous!r}, {path!r}.",
                path=source_path,
            )
        identities[key] = path
        parent = PurePosixPath(path).parent.as_posix()
        if parent not in directory_paths:
            raise ModuleCopySafetyError(
                "identity_rewrite",
                f"Module identity rewrite target {path!r} has no projected " f"parent directory {parent!r}.",
                path=source_path,
            )


def _read_source_file(
    source_module_fd: int,
    source_path: Path,
    expected: ModuleCopyFile,
) -> bytes:
    parts = PurePosixPath(expected.relative_path).parts
    parent_fd = _open_directory_parts(
        source_module_fd,
        parts[:-1],
        source_path,
    )
    descriptor: int | None = None
    try:
        try:
            descriptor = os.open(parts[-1], _FILE_FLAGS, dir_fd=parent_fd)
        except OSError as error:
            raise ModuleCopySafetyError(
                "source_unreadable",
                f"Module source file cannot be read safely: " f"{expected.relative_path}.",
                path=source_path / PurePosixPath(expected.relative_path),
            ) from error
        opened = os.fstat(descriptor)
        content = bytearray()
        digest = hashlib.sha256()
        while chunk := os.read(descriptor, 1024 * 1024):
            content.extend(chunk)
            digest.update(chunk)
        after = os.fstat(descriptor)
        if (
            not stat.S_ISREG(after.st_mode)
            or _identity(opened) != expected.identity
            or _identity(after) != expected.identity
            or after.st_size != expected.size_bytes
            or after.st_mtime_ns != expected.mtime_ns
            or stat.S_IMODE(after.st_mode) != expected.mode
            or digest.hexdigest() != expected.sha256
        ):
            raise ModuleCopySafetyError(
                "concurrent_change",
                f"Module source changed while identity content was read: " f"{expected.relative_path}.",
                path=source_path / PurePosixPath(expected.relative_path),
            )
        return bytes(content)
    except OSError as error:
        if isinstance(error, ModuleCopySafetyError):
            raise
        raise ModuleCopySafetyError(
            "source_unreadable",
            f"Module source file cannot be read safely: " f"{expected.relative_path}.",
            path=source_path / PurePosixPath(expected.relative_path),
        ) from error
    finally:
        if descriptor is not None:
            _close(descriptor)
        _close(parent_fd)


def _capture_directory(
    descriptor: int,
    root_path: Path,
    relative_path: PurePosixPath,
    *,
    root_device: int,
    directories: list[ModuleCopyDirectory],
    files: list[ModuleCopyFile],
    exclusions: list[ModuleCopyExclusion],
) -> None:
    before = os.fstat(descriptor)
    path = root_path / relative_path
    _require_same_device(root_device, before, path)
    relative_text = relative_path.as_posix() if relative_path.parts else "."
    directories.append(
        ModuleCopyDirectory(
            relative_path=relative_text,
            identity=_identity(before),
            mode=stat.S_IMODE(before.st_mode),
            mtime_ns=before.st_mtime_ns,
        )
    )
    names = sorted(os.listdir(descriptor))
    _require_portable_names(names, path)
    for name in names:
        child_relative = relative_path / name
        child_path = root_path / child_relative
        try:
            metadata = os.stat(name, dir_fd=descriptor, follow_symlinks=False)
        except OSError as error:
            raise ModuleCopySafetyError(
                "concurrent_change",
                f"Module entry changed during inventory: {child_path}.",
                path=child_path,
            ) from error
        if not relative_path.parts and name == _SYSTEM_TREE:
            _capture_system_metadata(
                descriptor,
                root_path,
                name,
                metadata,
                root_device=root_device,
                directories=directories,
                files=files,
                exclusions=exclusions,
            )
            continue
        if stat.S_ISLNK(metadata.st_mode):
            raise ModuleCopySafetyError(
                "symlink",
                f"Module duplication refuses symbolic links: {child_path}.",
                path=child_path,
            )
        _require_same_device(root_device, metadata, child_path)
        if stat.S_ISDIR(metadata.st_mode):
            child_fd = _open_required_directory(
                descriptor,
                name,
                child_path,
                code="concurrent_change",
            )
            try:
                _capture_directory(
                    child_fd,
                    root_path,
                    child_relative,
                    root_device=root_device,
                    directories=directories,
                    files=files,
                    exclusions=exclusions,
                )
            finally:
                _close(child_fd)
            continue
        if not stat.S_ISREG(metadata.st_mode):
            raise ModuleCopySafetyError(
                "special_entry",
                f"Module duplication supports only regular files and directories: {child_path}.",
                path=child_path,
            )
        files.append(
            _capture_file(
                descriptor,
                name,
                child_relative.as_posix(),
                child_path,
                expected=metadata,
            )
        )
    after_names = sorted(os.listdir(descriptor))
    after = os.fstat(descriptor)
    if (
        after_names != names
        or _identity(after) != _identity(before)
        or after.st_mtime_ns != before.st_mtime_ns
        or stat.S_IMODE(after.st_mode) != stat.S_IMODE(before.st_mode)
    ):
        raise ModuleCopySafetyError(
            "concurrent_change",
            f"Module directory changed during inventory: {path}.",
            path=path,
        )


def _capture_system_metadata(
    parent_fd: int,
    root_path: Path,
    name: str,
    metadata: os.stat_result,
    *,
    root_device: int,
    directories: list[ModuleCopyDirectory],
    files: list[ModuleCopyFile],
    exclusions: list[ModuleCopyExclusion],
) -> None:
    """Capture durable module settings while excluding transient system state."""

    relative_path = PurePosixPath(name)
    path = root_path / relative_path
    if not stat.S_ISDIR(metadata.st_mode):
        exclusions.append(
            ModuleCopyExclusion(
                relative_path=name,
                kind=_entry_kind(metadata.st_mode),
                identity=_identity(metadata),
                mode=stat.S_IMODE(metadata.st_mode),
                mtime_ns=metadata.st_mtime_ns,
            )
        )
        return

    descriptor = _open_required_directory(
        parent_fd,
        name,
        path,
        code="concurrent_change",
    )
    try:
        before = os.fstat(descriptor)
        names = sorted(os.listdir(descriptor))
        _require_portable_names(names, path)
        if not _DURABLE_SYSTEM_FILES.intersection(names):
            exclusions.append(
                ModuleCopyExclusion(
                    relative_path=name,
                    kind="directory",
                    identity=_identity(before),
                    mode=stat.S_IMODE(before.st_mode),
                    mtime_ns=before.st_mtime_ns,
                )
            )
            return

        _require_same_device(root_device, before, path)
        directories.append(
            ModuleCopyDirectory(
                relative_path=name,
                identity=_identity(before),
                mode=stat.S_IMODE(before.st_mode),
                mtime_ns=before.st_mtime_ns,
            )
        )
        for child_name in names:
            child_relative = relative_path / child_name
            child_path = root_path / child_relative
            try:
                child = os.stat(
                    child_name,
                    dir_fd=descriptor,
                    follow_symlinks=False,
                )
            except OSError as error:
                raise ModuleCopySafetyError(
                    "concurrent_change",
                    f"Module system entry changed during inventory: {child_path}.",
                    path=child_path,
                ) from error
            if child_name not in _DURABLE_SYSTEM_FILES:
                exclusions.append(
                    ModuleCopyExclusion(
                        relative_path=child_relative.as_posix(),
                        kind=_entry_kind(child.st_mode),
                        identity=_identity(child),
                        mode=stat.S_IMODE(child.st_mode),
                        mtime_ns=child.st_mtime_ns,
                    )
                )
                continue
            if stat.S_ISLNK(child.st_mode):
                raise ModuleCopySafetyError(
                    "symlink",
                    f"Module duplication refuses symbolic links: {child_path}.",
                    path=child_path,
                )
            _require_same_device(root_device, child, child_path)
            if not stat.S_ISREG(child.st_mode):
                raise ModuleCopySafetyError(
                    "special_entry",
                    "Durable module system metadata must be a regular file: " f"{child_path}.",
                    path=child_path,
                )
            files.append(
                _capture_file(
                    descriptor,
                    child_name,
                    child_relative.as_posix(),
                    child_path,
                    expected=child,
                )
            )
        after_names = sorted(os.listdir(descriptor))
        after = os.fstat(descriptor)
        if (
            after_names != names
            or _identity(after) != _identity(before)
            or after.st_mtime_ns != before.st_mtime_ns
            or stat.S_IMODE(after.st_mode) != stat.S_IMODE(before.st_mode)
        ):
            raise ModuleCopySafetyError(
                "concurrent_change",
                f"Module system metadata changed during inventory: {path}.",
                path=path,
            )
    finally:
        _close(descriptor)


def _capture_file(
    parent_fd: int,
    name: str,
    relative_path: str,
    path: Path,
    *,
    expected: os.stat_result,
) -> ModuleCopyFile:
    descriptor: int | None = None
    try:
        descriptor = os.open(name, _FILE_FLAGS, dir_fd=parent_fd)
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode) or _identity(opened) != _identity(expected):
            raise ModuleCopySafetyError(
                "concurrent_change",
                f"Module file changed before it could be read: {path}.",
                path=path,
            )
        digest = _hash_descriptor(descriptor)
        after = os.fstat(descriptor)
        if (
            _identity(after) != _identity(opened)
            or after.st_size != opened.st_size
            or after.st_mtime_ns != opened.st_mtime_ns
            or stat.S_IMODE(after.st_mode) != stat.S_IMODE(opened.st_mode)
        ):
            raise ModuleCopySafetyError(
                "concurrent_change",
                f"Module file changed while it was read: {path}.",
                path=path,
            )
        return ModuleCopyFile(
            relative_path=relative_path,
            identity=_identity(after),
            mode=stat.S_IMODE(after.st_mode),
            mtime_ns=after.st_mtime_ns,
            size_bytes=after.st_size,
            sha256=digest,
        )
    except ModuleCopySafetyError:
        raise
    except OSError as error:
        raise ModuleCopySafetyError(
            "source_unreadable",
            f"Module file cannot be read safely: {path}.",
            path=path,
        ) from error
    finally:
        if descriptor is not None:
            _close(descriptor)


def _capture_destination(
    authority: _RootAuthority,
    *,
    family: str,
    target_name: str,
    target_object_id: str,
) -> _Destination:
    modules_fd = _open_optional_directory(
        authority.descriptor,
        "modules",
        authority.path / "modules",
    )
    if modules_fd is None:
        return _Destination(
            modules_identity=None,
            family_identity=None,
            entry_count=0,
            entry_names_digest=_names_digest(()),
        )
    family_fd: int | None = None
    try:
        modules_metadata = os.fstat(modules_fd)
        _require_same_device(
            authority.identity[0],
            modules_metadata,
            authority.path / "modules",
        )
        family_fd = _open_optional_directory(
            modules_fd,
            family,
            authority.path / "modules" / family,
        )
        if family_fd is None:
            return _Destination(
                modules_identity=_identity(modules_metadata),
                family_identity=None,
                entry_count=0,
                entry_names_digest=_names_digest(()),
            )
        family_metadata = os.fstat(family_fd)
        _require_same_device(
            authority.identity[0],
            family_metadata,
            authority.path / "modules" / family,
        )
        names = tuple(sorted(os.listdir(family_fd)))
        aliases = _module_aliases(names, target_object_id)
        if aliases:
            raise ModuleCopySafetyError(
                "target_collision",
                (f"Module target {family}/{target_object_id} conflicts with " f"existing physical folder(s): {', '.join(aliases)}."),
                path=authority.path / "modules" / family / target_name,
            )
        after_names = tuple(sorted(os.listdir(family_fd)))
        after_family = os.fstat(family_fd)
        if after_names != names or _identity(after_family) != _identity(family_metadata) or after_family.st_mtime_ns != family_metadata.st_mtime_ns:
            raise ModuleCopySafetyError(
                "concurrent_change",
                "Destination module family changed during duplication planning.",
                path=authority.path / "modules" / family,
            )
        return _Destination(
            modules_identity=_identity(modules_metadata),
            family_identity=_identity(family_metadata),
            entry_count=len(names),
            entry_names_digest=_names_digest(names),
        )
    finally:
        if family_fd is not None:
            _close(family_fd)
        _close(modules_fd)


def _require_source_path_identity(
    authority: _RootAuthority,
    *,
    family: str,
    source_name: str,
    modules_identity: tuple[int, int],
    family_identity: tuple[int, int],
    module_identity: tuple[int, int],
) -> None:
    """Require the configured source path to remain bound to retained nodes."""

    modules_fd: int | None = None
    family_fd: int | None = None
    module_fd: int | None = None
    try:
        modules_fd = _open_required_directory(
            authority.descriptor,
            "modules",
            authority.path / "modules",
            code="concurrent_change",
        )
        family_fd = _open_required_directory(
            modules_fd,
            family,
            authority.path / "modules" / family,
            code="concurrent_change",
        )
        module_fd = _open_required_directory(
            family_fd,
            source_name,
            authority.path / "modules" / family / source_name,
            code="concurrent_change",
        )
        current = (
            _identity(os.fstat(modules_fd)),
            _identity(os.fstat(family_fd)),
            _identity(os.fstat(module_fd)),
        )
        expected = (
            modules_identity,
            family_identity,
            module_identity,
        )
        if current != expected:
            raise ModuleCopySafetyError(
                "concurrent_change",
                "Module source path changed during duplication.",
                path=authority.path / "modules" / family / source_name,
            )
    finally:
        for descriptor in (module_fd, family_fd, modules_fd):
            if descriptor is not None:
                _close(descriptor)


def _require_destination_target_path(
    authority: _RootAuthority,
    *,
    family: str,
    target_name: str,
    family_identity: tuple[int, int],
    target_identity: tuple[int, int],
) -> None:
    """Require the published target path to remain bound to created nodes."""

    modules_fd: int | None = None
    family_fd: int | None = None
    target_fd: int | None = None
    try:
        modules_fd = _open_required_directory(
            authority.descriptor,
            "modules",
            authority.path / "modules",
            code="concurrent_change",
        )
        family_fd = _open_required_directory(
            modules_fd,
            family,
            authority.path / "modules" / family,
            code="concurrent_change",
        )
        target_fd = _open_required_directory(
            family_fd,
            target_name,
            authority.path / "modules" / family / target_name,
            code="concurrent_change",
        )
        if _identity(os.fstat(family_fd)) != family_identity or _identity(os.fstat(target_fd)) != target_identity:
            raise ModuleCopySafetyError(
                "concurrent_change",
                "Duplicated module target path changed during publication.",
                path=authority.path / "modules" / family / target_name,
            )
    finally:
        for descriptor in (target_fd, family_fd, modules_fd):
            if descriptor is not None:
                _close(descriptor)


def _stage_source_file(
    source_module_fd: int,
    transaction_fd: int,
    expected: ModuleCopyFile,
    *,
    target: ModuleCopyTargetFile,
    context: ModuleIdentityContext,
    identity_rewriter: ModuleIdentityRewriter | None,
    stage_name: str,
    source_path: Path,
) -> _StageFile:
    rewritten = _target_file_content(
        source_module_fd,
        source_path,
        expected,
        context=context,
        identity_rewriter=identity_rewriter,
    )
    if rewritten is not None:
        if len(rewritten) != target.size_bytes or hashlib.sha256(rewritten).hexdigest() != target.sha256:
            raise OSError(
                errno.EAGAIN,
                f"Module identity rewrite changed after planning: " f"{expected.relative_path}.",
            )
        return _stage_rewritten_file(
            transaction_fd,
            target,
            rewritten,
            stage_name=stage_name,
        )
    parts = PurePosixPath(expected.relative_path).parts
    parent_fd = _open_directory_parts(
        source_module_fd,
        parts[:-1],
        source_path,
    )
    source_fd: int | None = None
    stage_fd: int | None = None
    staged = False
    try:
        metadata = os.stat(
            parts[-1],
            dir_fd=parent_fd,
            follow_symlinks=False,
        )
        if (
            not stat.S_ISREG(metadata.st_mode)
            or _identity(metadata) != expected.identity
            or metadata.st_size != expected.size_bytes
            or metadata.st_mtime_ns != expected.mtime_ns
            or stat.S_IMODE(metadata.st_mode) != expected.mode
        ):
            raise OSError(
                errno.EAGAIN,
                f"Module source changed before staging: {expected.relative_path}.",
            )
        source_fd = os.open(parts[-1], _FILE_FLAGS, dir_fd=parent_fd)
        opened = os.fstat(source_fd)
        if _identity(opened) != expected.identity:
            raise OSError(
                errno.EAGAIN,
                f"Module source changed while staging: {expected.relative_path}.",
            )
        stage_fd = os.open(
            stage_name,
            _CREATE_FILE_FLAGS,
            0o600,
            dir_fd=transaction_fd,
        )
        digest = hashlib.sha256()
        size = 0
        while chunk := os.read(source_fd, 1024 * 1024):
            digest.update(chunk)
            size += len(chunk)
            _write_all(stage_fd, chunk)
        after = os.fstat(source_fd)
        if (
            _identity(after) != expected.identity
            or after.st_size != expected.size_bytes
            or after.st_mtime_ns != expected.mtime_ns
            or stat.S_IMODE(after.st_mode) != expected.mode
            or size != expected.size_bytes
            or digest.hexdigest() != expected.sha256
        ):
            raise OSError(
                errno.EAGAIN,
                f"Module source changed while staging: {expected.relative_path}.",
            )
        os.fchmod(stage_fd, expected.mode)
        os.fsync(stage_fd)
        staged_metadata = os.fstat(stage_fd)
        staged = True
        return _StageFile(
            name=stage_name,
            identity=_identity(staged_metadata),
            size_bytes=staged_metadata.st_size,
            sha256=target.sha256,
        )
    finally:
        if stage_fd is not None:
            _close(stage_fd)
        if not staged:
            try:
                os.unlink(stage_name, dir_fd=transaction_fd)
            except FileNotFoundError:
                pass
        if source_fd is not None:
            _close(source_fd)
        _close(parent_fd)


def _stage_rewritten_file(
    transaction_fd: int,
    target: ModuleCopyTargetFile,
    content: bytes,
    *,
    stage_name: str,
) -> _StageFile:
    stage_fd: int | None = None
    staged = False
    try:
        stage_fd = os.open(
            stage_name,
            _CREATE_FILE_FLAGS,
            0o600,
            dir_fd=transaction_fd,
        )
        _write_all(stage_fd, content)
        os.fchmod(stage_fd, target.mode)
        os.fsync(stage_fd)
        metadata = os.fstat(stage_fd)
        if metadata.st_size != target.size_bytes or hashlib.sha256(content).hexdigest() != target.sha256:
            raise OSError(
                errno.EAGAIN,
                f"Staged identity rewrite changed for {target.source_relative_path}.",
            )
        staged = True
        return _StageFile(
            name=stage_name,
            identity=_identity(metadata),
            size_bytes=metadata.st_size,
            sha256=target.sha256,
        )
    finally:
        if stage_fd is not None:
            _close(stage_fd)
        if not staged:
            try:
                os.unlink(stage_name, dir_fd=transaction_fd)
            except FileNotFoundError:
                pass


def _require_destination_precondition(
    destination: _RootAuthority,
    modules_fd: int,
    family_fd: int,
    expected: ModuleCopySnapshot,
    *,
    target_name: str,
    target_object_id: str,
) -> None:
    modules_identity = _identity(os.fstat(modules_fd))
    family_identity = _identity(os.fstat(family_fd))
    if expected.destination_modules_identity is not None and modules_identity != expected.destination_modules_identity:
        raise OSError(errno.EAGAIN, "Destination modules directory identity changed.")
    if expected.destination_family_identity is not None and family_identity != expected.destination_family_identity:
        raise OSError(errno.EAGAIN, "Destination family directory identity changed.")
    names = tuple(sorted(os.listdir(family_fd)))
    if expected.destination_family_identity is not None and (
        len(names) != expected.destination_entry_count or _names_digest(names) != expected.destination_entry_names_digest
    ):
        raise OSError(errno.EAGAIN, "Destination module family changed after planning.")
    aliases = _module_aliases(names, target_object_id)
    if aliases:
        raise FileExistsError(f"Module target {target_object_id!r} already exists: {', '.join(aliases)}.")
    destination.verify_path()


def _require_target_alias_state(
    family_fd: int,
    *,
    target_name: str,
    target_object_id: str,
) -> None:
    aliases = _module_aliases(tuple(os.listdir(family_fd)), target_object_id)
    if aliases != (target_name,):
        raise OSError(
            errno.EAGAIN,
            f"Duplicated module target alias state changed: {', '.join(aliases) or 'missing'}.",
        )


def _link_stage_file(
    transaction_fd: int,
    stage_name: str,
    target_parent_fd: int,
    target_name: str,
) -> None:
    os.link(
        stage_name,
        target_name,
        src_dir_fd=transaction_fd,
        dst_dir_fd=target_parent_fd,
        follow_symlinks=False,
    )


def _rollback_target(
    family_fd: int,
    target_name: str,
    target_identity: tuple[int, int],
    transaction_fd: int,
    *,
    transaction_path: Path,
    expected: ModuleCopySnapshot,
    staged: list[_StageFile],
    directory_identities: dict[str, tuple[int, int]],
    root_device: int,
) -> None:
    current = os.stat(
        target_name,
        dir_fd=family_fd,
        follow_symlinks=False,
    )
    if not stat.S_ISDIR(current.st_mode) or _identity(current) != target_identity:
        raise OSError(f"Duplicate target identity changed; recovery may remain at " f"{transaction_path.parent.parent.parent / 'modules' / target_name}.")
    recovery_name = "module.rollback"
    os.rename(
        target_name,
        recovery_name,
        src_dir_fd=family_fd,
        dst_dir_fd=transaction_fd,
    )
    recovery_fd = _open_required_directory(
        transaction_fd,
        recovery_name,
        transaction_path / recovery_name,
        code="concurrent_change",
    )
    try:
        recovered = _capture_tree(
            recovery_fd,
            transaction_path / recovery_name,
            root_device=root_device,
        )
    finally:
        _close(recovery_fd)
    if not _tree_is_owned_subset(
        recovered,
        expected,
        staged,
        directory_identities,
    ):
        raise OSError(f"Changed duplicate target was preserved for recovery at " f"{transaction_path / recovery_name}.")
    _delete_captured_tree(
        transaction_fd,
        recovery_name,
        recovered,
        transaction_path / recovery_name,
    )


def _tree_is_owned_subset(
    tree: _Tree,
    expected: ModuleCopySnapshot,
    staged: list[_StageFile],
    directory_identities: dict[str, tuple[int, int]],
) -> bool:
    if tree.exclusions:
        return False
    expected_directories = {
        item.relative_path: (
            item.mode,
            directory_identities.get(item.relative_path),
        )
        for item in expected.target_directories
    }
    expected_files = {
        item.relative_path: (
            item.mode,
            stage.size_bytes,
            stage.sha256,
            stage.identity,
        )
        for item, stage in zip(expected.target_files, staged, strict=True)
    }
    return all(expected_directories.get(item.relative_path) == (item.mode, item.identity) for item in tree.directories) and all(
        expected_files.get(item.relative_path) == (item.mode, item.size_bytes, item.sha256, item.identity) for item in tree.files
    )


def _target_matches_install(
    tree: _Tree,
    expected: ModuleCopySnapshot,
    staged: list[_StageFile],
    directory_identities: dict[str, tuple[int, int]],
) -> bool:
    return (
        tree.content_digest == expected.target_content_digest
        and len(tree.directories) == len(expected.target_directories)
        and len(tree.files) == len(expected.target_files)
        and _tree_is_owned_subset(
            tree,
            expected,
            staged,
            directory_identities,
        )
    )


def _delete_captured_tree(
    parent_fd: int,
    name: str,
    captured: _Tree,
    path: Path,
) -> None:
    root_fd = _open_required_directory(
        parent_fd,
        name,
        path,
        code="concurrent_change",
    )
    descriptors: dict[str, int] = {".": root_fd}
    try:
        for item in captured.directories:
            if item.relative_path == ".":
                continue
            parent_path, child_name = _parent_and_name(item.relative_path)
            child_fd = _open_required_directory(
                descriptors[parent_path],
                child_name,
                path / PurePosixPath(item.relative_path),
                code="concurrent_change",
            )
            if _identity(os.fstat(child_fd)) != item.identity:
                raise OSError(f"Recovery directory changed before cleanup: {item.relative_path}.")
            descriptors[item.relative_path] = child_fd
        for item in captured.files:
            parent_path, child_name = _parent_and_name(item.relative_path)
            metadata = os.stat(
                child_name,
                dir_fd=descriptors[parent_path],
                follow_symlinks=False,
            )
            if _identity(metadata) != item.identity:
                raise OSError(f"Recovery file changed before cleanup: {item.relative_path}.")
            os.unlink(child_name, dir_fd=descriptors[parent_path])
        for item in sorted(
            captured.directories,
            key=lambda row: (row.relative_path.count("/"), row.relative_path),
            reverse=True,
        ):
            descriptor = descriptors[item.relative_path]
            if os.listdir(descriptor):
                raise OSError(f"Recovery directory gained unexpected contents: {item.relative_path}.")
            if item.relative_path == ".":
                continue
            parent_path, child_name = _parent_and_name(item.relative_path)
            _close(descriptor)
            descriptors[item.relative_path] = -1
            os.rmdir(child_name, dir_fd=descriptors[parent_path])
        _close(root_fd)
        descriptors["."] = -1
        os.rmdir(name, dir_fd=parent_fd)
    finally:
        for descriptor in descriptors.values():
            if descriptor >= 0:
                _close(descriptor)


def _cleanup_stage_files(
    transaction_fd: int,
    staged: list[_StageFile],
) -> None:
    for item in staged:
        _require_file_fingerprint(
            transaction_fd,
            item.name,
            expected=item,
            label=f"module-copy stage {item.name}",
        )
    for item in staged:
        os.unlink(item.name, dir_fd=transaction_fd)


def _remove_transaction(
    transactions_fd: int,
    transaction_name: str,
    expected_identity: tuple[int, int],
) -> None:
    transaction_fd = _open_required_directory(
        transactions_fd,
        transaction_name,
        Path(transaction_name),
        code="concurrent_change",
    )
    try:
        if _identity(os.fstat(transaction_fd)) != expected_identity:
            raise OSError(f"Module-copy transaction identity changed: {transaction_name}.")
        if os.listdir(transaction_fd):
            raise OSError(f"Module-copy transaction is not empty: {transaction_name}.")
    finally:
        _close(transaction_fd)
    cleanup_name = f"{transaction_name}.cleanup-{uuid4().hex}"
    os.rename(
        transaction_name,
        cleanup_name,
        src_dir_fd=transactions_fd,
        dst_dir_fd=transactions_fd,
    )
    moved = os.stat(
        cleanup_name,
        dir_fd=transactions_fd,
        follow_symlinks=False,
    )
    if not stat.S_ISDIR(moved.st_mode) or _identity(moved) != expected_identity:
        raise OSError(f"Changed module-copy transaction was preserved as {cleanup_name}.")
    os.rmdir(cleanup_name, dir_fd=transactions_fd)


def _open_directory_parts(
    root_fd: int,
    parts: tuple[str, ...],
    root_path: Path,
) -> int:
    current = os.dup(root_fd)
    try:
        for index, part in enumerate(parts):
            child = _open_required_directory(
                current,
                part,
                root_path.joinpath(*parts[: index + 1]),
                code="concurrent_change",
            )
            _close(current)
            current = child
        return current
    except BaseException:
        _close(current)
        raise


def _require_file_fingerprint(
    parent_fd: int,
    name: str,
    *,
    expected: _StageFile,
    label: str,
) -> None:
    descriptor: int | None = None
    try:
        descriptor = os.open(name, _FILE_FLAGS, dir_fd=parent_fd)
        metadata = os.fstat(descriptor)
        if (
            not stat.S_ISREG(metadata.st_mode)
            or _identity(metadata) != expected.identity
            or metadata.st_size != expected.size_bytes
            or _hash_descriptor(descriptor) != expected.sha256
        ):
            raise OSError(f"{label} changed before it could be verified.")
    finally:
        if descriptor is not None:
            _close(descriptor)


def _require_portable_names(names: list[str], path: Path) -> None:
    identities: dict[str, str] = {}
    for name in names:
        if unicodedata.normalize("NFC", name) != name:
            raise ModuleCopySafetyError(
                "nonportable_name",
                f"Module entry is not NFC-normalized: {path / name}.",
                path=path / name,
            )
        if error := windows_portable_component_error(name):
            raise ModuleCopySafetyError(
                "nonportable_name",
                f"Module entry is not portable to Windows because it {error}: {path / name}.",
                path=path / name,
            )
        if len(os.fsencode(name)) > 255:
            raise ModuleCopySafetyError(
                "nonportable_name",
                f"Module entry exceeds the portable 255-byte filename limit: {path / name}.",
                path=path / name,
            )
        key = _portable_key(name)
        previous = identities.get(key)
        if previous is not None:
            raise ModuleCopySafetyError(
                "portable_collision",
                f"Module entries collide by case or Unicode normalization: {path / previous}, {path / name}.",
                path=path,
            )
        identities[key] = name
    system_alias = identities.get(_portable_key(_SYSTEM_TREE))
    if system_alias is not None and system_alias != _SYSTEM_TREE:
        raise ModuleCopySafetyError(
            "portable_collision",
            f"Module system tree {_SYSTEM_TREE!r} has a non-excludable portable alias: {path / system_alias}.",
            path=path / system_alias,
        )


def _require_same_device(
    root_device: int,
    metadata: os.stat_result,
    path: Path,
) -> None:
    if metadata.st_dev != root_device:
        raise ModuleCopySafetyError(
            "filesystem_boundary",
            f"Module duplication refuses a nested filesystem boundary: {path}.",
            path=path,
        )


def _tree_matches_snapshot(
    tree: _Tree,
    expected: ModuleCopySnapshot,
) -> bool:
    return (
        tree.directories == expected.directories
        and tree.files == expected.files
        and tree.exclusions == expected.exclusions
        and tree.tree_digest == expected.tree_digest
        and tree.content_digest == expected.content_digest
    )


def _target_directory_mode(
    directories: tuple[ModuleCopyTargetDirectory, ...],
    relative_path: str,
) -> int:
    for item in directories:
        if item.relative_path == relative_path:
            return item.mode
    raise AssertionError(f"Module-copy plan has no directory {relative_path!r}.")


def _parent_and_name(relative_path: str) -> tuple[str, str]:
    path = PurePosixPath(relative_path)
    parent = path.parent.as_posix()
    return ("." if parent == "." else parent), path.name


def _module_aliases(
    names: tuple[str, ...],
    target_object_id: str,
) -> tuple[str, ...]:
    target_key = _portable_key(target_object_id)
    return tuple(sorted(name for name in names if _portable_key(_folder_object_id(name)) == target_key))


def _folder_object_id(name: str) -> str:
    return name.split(" - ", 1)[0].strip()


def _portable_key(value: str) -> str:
    return unicodedata.normalize("NFC", value).casefold()


def _portable_relative_key(value: str) -> str:
    return "/".join(_portable_key(part) for part in PurePosixPath(value).parts)


def _identity(metadata: os.stat_result) -> tuple[int, int]:
    return metadata.st_dev, metadata.st_ino


def _entry_kind(mode: int) -> str:
    if stat.S_ISDIR(mode):
        return "directory"
    if stat.S_ISREG(mode):
        return "file"
    if stat.S_ISLNK(mode):
        return "symlink"
    return "special"


def _hash_descriptor(descriptor: int) -> str:
    os.lseek(descriptor, 0, os.SEEK_SET)
    digest = hashlib.sha256()
    while chunk := os.read(descriptor, 1024 * 1024):
        digest.update(chunk)
    return digest.hexdigest()


def _write_all(descriptor: int, payload: bytes) -> None:
    view = memoryview(payload)
    while view:
        written = os.write(descriptor, view)
        if written <= 0:
            raise OSError("Module-copy stage write made no progress.")
        view = view[written:]


def _digest_json(value: object) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _names_digest(names: tuple[str, ...]) -> str:
    return _digest_json(list(names))


def _close(descriptor: int) -> None:
    try:
        os.close(descriptor)
    except OSError:
        pass
