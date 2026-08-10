"""Descriptor-anchored filesystem boundary for generated build data."""

from __future__ import annotations

import errno
import hashlib
import os
import stat
import sys
import unicodedata
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
from typing import BinaryIO, ContextManager, Iterator
from uuid import uuid4

_DIRECTORY_FLAGS = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
_ANCHORED_PUBLICATION_SUPPORTED = (
    os.open in os.supports_dir_fd
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


class AnchoredDirectory:
    """Open directory authority retained for one publication transaction."""

    def __init__(self, requested_path: Path, path: Path, descriptor: int) -> None:
        self.requested_path = requested_path
        self.path = path
        self._descriptor = descriptor
        root_stat = os.fstat(descriptor)
        self._identity = (root_stat.st_dev, root_stat.st_ino)

    def close(self) -> None:
        """Close the retained directory descriptor."""

        if self._descriptor < 0:
            return
        os.close(self._descriptor)
        self._descriptor = -1

    @property
    def identity(self) -> tuple[int, int]:
        """Return the retained filesystem device and inode identity."""

        return self._identity

    def is_empty(self) -> bool:
        """Return whether the retained directory contains no entries."""

        self._require_open()
        return not os.listdir(self._descriptor)

    def entry_exists(self, relative_path: str | PurePosixPath) -> bool:
        """Check for any leaf type without opening or following the leaf."""

        parts = _relative_parts(relative_path)
        parent = self._open_parent(parts[:-1], create=False)
        if parent is None:
            return False
        try:
            try:
                os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
            except FileNotFoundError:
                return False
            return True
        finally:
            os.close(parent)

    def same_entry(
        self,
        left_path: str | PurePosixPath,
        right_path: str | PurePosixPath,
    ) -> bool:
        """Return whether two relative names resolve to the same regular file."""

        left_parts = _relative_parts(left_path)
        right_parts = _relative_parts(right_path)
        left_parent = self._open_parent(left_parts[:-1], create=False)
        if left_parent is None:
            return False
        right_parent = self._open_parent(right_parts[:-1], create=False)
        if right_parent is None:
            os.close(left_parent)
            return False
        try:
            try:
                left = os.stat(
                    left_parts[-1],
                    dir_fd=left_parent,
                    follow_symlinks=False,
                )
                right = os.stat(
                    right_parts[-1],
                    dir_fd=right_parent,
                    follow_symlinks=False,
                )
            except FileNotFoundError:
                return False
            return stat.S_ISREG(left.st_mode) and stat.S_ISREG(right.st_mode) and (left.st_dev, left.st_ino) == (right.st_dev, right.st_ino)
        finally:
            os.close(right_parent)
            os.close(left_parent)

    def verify_path(self) -> None:
        """Reject a root path replaced after this authority was opened."""

        self._require_open()
        try:
            descriptor = _open_directory_path(self.path, create=False)
        except OSError as error:
            raise ValueError(f"Generated publication root changed during the build: {self.requested_path}.") from error
        try:
            current = os.fstat(descriptor)
        finally:
            os.close(descriptor)
        if (current.st_dev, current.st_ino) != self._identity:
            raise ValueError(f"Generated publication root changed during the build: {self.requested_path}.")

    def read_bytes(self, relative_path: str | PurePosixPath) -> bytes | None:
        """Read one regular file without following generated-tree symlinks."""

        parts = _relative_parts(relative_path)
        parent = self._open_parent(parts[:-1], create=False)
        if parent is None:
            return None
        descriptor: int | None = None
        try:
            try:
                expected_metadata = os.stat(
                    parts[-1],
                    dir_fd=parent,
                    follow_symlinks=False,
                )
            except FileNotFoundError:
                return None
            if not stat.S_ISREG(expected_metadata.st_mode):
                raise ValueError(f"Generated publication path is not a regular file: {self.path / PurePosixPath(*parts)}.")
            try:
                descriptor = os.open(
                    parts[-1],
                    os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_CLOEXEC", 0),
                    dir_fd=parent,
                )
            except FileNotFoundError:
                return None
            except OSError as error:
                raise ValueError(f"Generated publication file changed or crosses a symlink: {self.path / PurePosixPath(*parts)}.") from error
            opened_metadata = os.fstat(descriptor)
            if not stat.S_ISREG(opened_metadata.st_mode) or (opened_metadata.st_dev, opened_metadata.st_ino) != (
                expected_metadata.st_dev,
                expected_metadata.st_ino,
            ):
                raise ValueError(f"Generated publication file changed before it could be read: {self.path / PurePosixPath(*parts)}.")
            with os.fdopen(descriptor, "rb", closefd=False) as handle:
                return handle.read()
        finally:
            if descriptor is not None:
                os.close(descriptor)
            os.close(parent)

    def file_sha256_matches(
        self,
        relative_path: str | PurePosixPath,
        expected_sha256: str,
    ) -> bool | None:
        """Compare one regular file with an exact SHA-256 without following links."""

        parts = _relative_parts(relative_path)
        parent = self._open_parent(parts[:-1], create=False)
        if parent is None:
            return None
        descriptor: int | None = None
        try:
            try:
                expected_metadata = os.stat(
                    parts[-1],
                    dir_fd=parent,
                    follow_symlinks=False,
                )
            except FileNotFoundError:
                return None
            if not stat.S_ISREG(expected_metadata.st_mode):
                raise ValueError(f"Generated publication path is not a regular file: " f"{self.path / PurePosixPath(*parts)}.")
            try:
                descriptor = os.open(
                    parts[-1],
                    os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_CLOEXEC", 0),
                    dir_fd=parent,
                )
            except FileNotFoundError:
                return None
            except OSError as error:
                raise ValueError("Generated publication file changed or crosses a symlink: " f"{self.path / PurePosixPath(*parts)}.") from error
            opened_metadata = os.fstat(descriptor)
            if not stat.S_ISREG(opened_metadata.st_mode) or (
                opened_metadata.st_dev,
                opened_metadata.st_ino,
            ) != (
                expected_metadata.st_dev,
                expected_metadata.st_ino,
            ):
                raise ValueError("Generated publication file changed before it could be hashed: " f"{self.path / PurePosixPath(*parts)}.")
            digest = hashlib.sha256()
            while chunk := os.read(descriptor, 1024 * 1024):
                digest.update(chunk)
            return digest.hexdigest() == expected_sha256
        finally:
            if descriptor is not None:
                os.close(descriptor)
            os.close(parent)

    def file_matches(
        self,
        relative_path: str | PurePosixPath,
        source: Path,
    ) -> bool | None:
        """Compare one regular target with a staged file using bounded reads."""

        parts = _relative_parts(relative_path)
        try:
            source_metadata = source.lstat()
        except OSError as error:
            raise ValueError(f"Staged artifact cannot be read: {source}.") from error
        if not stat.S_ISREG(source_metadata.st_mode):
            raise ValueError(f"Staged artifact cannot be opened as a regular file: {source}.")
        source_descriptor = _open_verified_regular_file(
            source,
            expected=source_metadata,
            label=f"Staged artifact changed before comparison: {source}.",
        )
        parent = self._open_parent(parts[:-1], create=False)
        if parent is None:
            os.close(source_descriptor)
            return None
        target_descriptor: int | None = None
        try:
            try:
                target_metadata = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
            except FileNotFoundError:
                return None
            if not stat.S_ISREG(target_metadata.st_mode):
                raise ValueError(f"Generated publication path is not a regular file: {self.path / PurePosixPath(*parts)}.")
            try:
                target_descriptor = os.open(
                    parts[-1],
                    os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_CLOEXEC", 0),
                    dir_fd=parent,
                )
            except FileNotFoundError:
                return None
            except OSError as error:
                raise ValueError(f"Generated publication file changed before comparison: {self.path / PurePosixPath(*parts)}.") from error
            opened_target = os.fstat(target_descriptor)
            if not stat.S_ISREG(opened_target.st_mode) or (opened_target.st_dev, opened_target.st_ino) != (
                target_metadata.st_dev,
                target_metadata.st_ino,
            ):
                raise ValueError(f"Generated publication file changed before comparison: {self.path / PurePosixPath(*parts)}.")
            if opened_target.st_size != source_metadata.st_size:
                return False
            while True:
                source_chunk = os.read(source_descriptor, 1024 * 1024)
                target_chunk = os.read(target_descriptor, 1024 * 1024)
                if source_chunk != target_chunk:
                    return False
                if not source_chunk:
                    return True
        finally:
            os.close(source_descriptor)
            if target_descriptor is not None:
                os.close(target_descriptor)
            os.close(parent)

    def write_bytes(
        self,
        relative_path: str | PurePosixPath,
        payload: bytes,
        *,
        mode: int = 0o644,
        replace: bool = True,
    ) -> Path:
        """Atomically publish bytes, optionally requiring an absent target."""

        parts = _relative_parts(relative_path)
        parent = self._open_parent(parts[:-1], create=True)
        if parent is None:
            raise AssertionError("Creating a publication parent returned no descriptor.")
        try:
            self._write(
                parent,
                parts[-1],
                payload=payload,
                mode=mode,
                replace=replace,
            )
        finally:
            os.close(parent)
        return self.requested_path.joinpath(*parts)

    def publish_file(
        self,
        relative_path: str | PurePosixPath,
        source: Path,
        *,
        replace: bool = True,
    ) -> Path:
        """Atomically publish a staged file, optionally requiring no target."""

        parts = _relative_parts(relative_path)
        try:
            source_metadata = source.lstat()
        except OSError as error:
            raise ValueError(f"Staged artifact cannot be read: {source}.") from error
        if not stat.S_ISREG(source_metadata.st_mode):
            raise ValueError(f"Staged artifact cannot be opened as a regular file: {source}.")
        source_descriptor: int | None = None
        try:
            source_descriptor = os.open(
                source,
                os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0),
            )
        except OSError as error:
            raise ValueError(f"Staged artifact cannot be opened: {source}.") from error
        opened_metadata = os.fstat(source_descriptor)
        if not stat.S_ISREG(opened_metadata.st_mode) or (
            opened_metadata.st_dev,
            opened_metadata.st_ino,
        ) != (
            source_metadata.st_dev,
            source_metadata.st_ino,
        ):
            os.close(source_descriptor)
            raise ValueError(f"Staged artifact changed before publication: {source}.")
        source_handle = os.fdopen(source_descriptor, "rb")
        parent = self._open_parent(parts[:-1], create=True)
        if parent is None:
            source_handle.close()
            raise AssertionError("Creating a publication parent returned no descriptor.")
        try:
            self._write(
                parent,
                parts[-1],
                source=source_handle,
                mode=stat.S_IMODE(source_metadata.st_mode),
                replace=replace,
            )
        finally:
            source_handle.close()
            os.close(parent)
        return self.requested_path.joinpath(*parts)

    def normalize_path_spelling(
        self,
        previous_path: str | PurePosixPath,
        current_path: str | PurePosixPath,
    ) -> bool:
        """Normalize every case-aliased component to its tracked spelling."""

        previous_parts = _relative_parts(previous_path)
        current_parts = _relative_parts(current_path)
        if len(previous_parts) != len(current_parts) or tuple(_path_part_identity(part) for part in previous_parts) != tuple(
            _path_part_identity(part) for part in current_parts
        ):
            raise ValueError("Generated publication spelling transition must preserve " f"path identity: {previous_path!s} -> {current_path!s}.")
        descriptor = os.dup(self._descriptor)
        try:
            for index, (previous_name, current_name) in enumerate(zip(previous_parts, current_parts, strict=True)):
                names = os.listdir(descriptor)
                if current_name not in names:
                    if previous_name not in names:
                        return False
                    try:
                        previous = os.stat(
                            previous_name,
                            dir_fd=descriptor,
                            follow_symlinks=False,
                        )
                        current = os.stat(
                            current_name,
                            dir_fd=descriptor,
                            follow_symlinks=False,
                        )
                    except FileNotFoundError:
                        return False
                    if (previous.st_dev, previous.st_ino) != (
                        current.st_dev,
                        current.st_ino,
                    ):
                        return False
                    os.rename(
                        previous_name,
                        current_name,
                        src_dir_fd=descriptor,
                        dst_dir_fd=descriptor,
                    )
                    normalized = os.stat(
                        current_name,
                        dir_fd=descriptor,
                        follow_symlinks=False,
                    )
                    if (
                        normalized.st_dev,
                        normalized.st_ino,
                    ) != (
                        current.st_dev,
                        current.st_ino,
                    ) or current_name not in os.listdir(descriptor):
                        raise ValueError(
                            "Generated publication path could not normalize "
                            f"its tracked spelling: "
                            f"{self.requested_path / PurePosixPath(*current_parts)}."
                        )
                    _fsync(descriptor)
                if index == len(current_parts) - 1:
                    metadata = os.stat(
                        current_name,
                        dir_fd=descriptor,
                        follow_symlinks=False,
                    )
                    return stat.S_ISREG(metadata.st_mode)
                try:
                    child = os.open(
                        current_name,
                        _DIRECTORY_FLAGS,
                        dir_fd=descriptor,
                    )
                except OSError as error:
                    raise ValueError(
                        "Generated publication path crosses a symlink or "
                        "non-directory while normalizing tracked spelling: "
                        f"{self.requested_path / PurePosixPath(*current_parts)}."
                    ) from error
                os.close(descriptor)
                descriptor = child
            return False
        finally:
            os.close(descriptor)

    def delete_file(
        self,
        relative_path: str | PurePosixPath,
        *,
        exact_spelling: bool = False,
        prune_empty_parents: bool = True,
    ) -> bool:
        """Delete one regular generated file and optionally prune empty parents."""

        parts = _relative_parts(relative_path)
        self._require_open()
        descriptors = [os.dup(self._descriptor)]
        try:
            for part in parts[:-1]:
                try:
                    descriptor = os.open(part, _DIRECTORY_FLAGS, dir_fd=descriptors[-1])
                except FileNotFoundError:
                    return False
                except OSError as error:
                    raise ValueError(
                        f"Generated publication path crosses a symlink or changed parent below {self.requested_path}: " f"{PurePosixPath(*parts)}."
                    ) from error
                descriptors.append(descriptor)
            if exact_spelling and parts[-1] not in os.listdir(descriptors[-1]):
                return False
            try:
                metadata = os.stat(parts[-1], dir_fd=descriptors[-1], follow_symlinks=False)
            except FileNotFoundError:
                return False
            if stat.S_ISDIR(metadata.st_mode):
                raise ValueError(f"Generated publication file path is a directory, refusing to delete it: " f"{self.requested_path / PurePosixPath(*parts)}.")
            os.unlink(parts[-1], dir_fd=descriptors[-1])
            if prune_empty_parents:
                for index in range(len(parts) - 2, -1, -1):
                    try:
                        os.rmdir(parts[index], dir_fd=descriptors[index])
                    except OSError:
                        break
            return True
        finally:
            for descriptor in reversed(descriptors):
                os.close(descriptor)

    def clear(self) -> None:
        """Remove all entries below this authority without deleting the root."""

        self._require_open()
        mount_table = _linux_mount_table()
        root_mount_id = _descriptor_mount_id(self._descriptor, mount_table)
        if sys.platform.startswith("linux") and root_mount_id is None:
            raise ValueError("Cannot verify Linux mount boundaries for generated-root full clean.")
        self._clear_directory(
            self._descriptor,
            relative_path=PurePosixPath(),
            root_device=self._identity[0],
            root_mount_id=root_mount_id,
            mount_table=mount_table,
        )

    def _clear_directory(
        self,
        descriptor: int,
        *,
        relative_path: PurePosixPath,
        root_device: int,
        root_mount_id: int | None,
        mount_table: tuple[tuple[int, str], ...],
    ) -> None:
        """Empty one retained directory without following or crossing entries."""

        directory_metadata = os.fstat(descriptor)
        current_mount_id = _descriptor_mount_id(descriptor, mount_table)
        if (
            not stat.S_ISDIR(directory_metadata.st_mode)
            or directory_metadata.st_dev != root_device
            or (root_mount_id is not None and current_mount_id != root_mount_id)
        ):
            path = self.requested_path / relative_path
            raise ValueError(f"Generated publication directory crosses a filesystem boundary during full clean: {path}.")
        try:
            names = sorted(os.listdir(descriptor))
            for name in names:
                child_path = relative_path / name
                self._clear_entry(
                    descriptor,
                    name=name,
                    relative_path=child_path,
                    root_device=root_device,
                    root_mount_id=root_mount_id,
                    mount_table=mount_table,
                )
        finally:
            _fsync(descriptor)

    def _clear_entry(
        self,
        parent: int,
        *,
        name: str,
        relative_path: PurePosixPath,
        root_device: int,
        root_mount_id: int | None,
        mount_table: tuple[tuple[int, str], ...],
    ) -> None:
        """Remove one direct child while retaining its descriptor authority."""

        path = self.requested_path / relative_path
        try:
            metadata = os.stat(name, dir_fd=parent, follow_symlinks=False)
        except FileNotFoundError as error:
            raise ValueError(f"Generated publication entry changed during full clean: {path}.") from error
        if metadata.st_dev != root_device:
            raise ValueError(f"Generated publication entry crosses a filesystem boundary, refusing full clean: {path}.")
        if not stat.S_ISDIR(metadata.st_mode):
            try:
                os.unlink(name, dir_fd=parent)
            except FileNotFoundError as error:
                raise ValueError(f"Generated publication entry changed during full clean: {path}.") from error
            return

        try:
            descriptor = os.open(name, _DIRECTORY_FLAGS, dir_fd=parent)
        except OSError as error:
            raise ValueError(f"Generated publication directory changed, crosses a symlink, or cannot be opened during full clean: {path}.") from error
        try:
            opened_metadata = os.fstat(descriptor)
            if (
                not stat.S_ISDIR(opened_metadata.st_mode)
                or opened_metadata.st_dev != root_device
                or (root_mount_id is not None and _descriptor_mount_id(descriptor, mount_table) != root_mount_id)
                or (opened_metadata.st_dev, opened_metadata.st_ino) != (metadata.st_dev, metadata.st_ino)
            ):
                raise ValueError(f"Generated publication directory changed or crosses a filesystem boundary during full clean: {path}.")
            self._clear_directory(
                descriptor,
                relative_path=relative_path,
                root_device=root_device,
                root_mount_id=root_mount_id,
                mount_table=mount_table,
            )
            try:
                current_metadata = os.stat(name, dir_fd=parent, follow_symlinks=False)
            except FileNotFoundError as error:
                raise ValueError(f"Generated publication directory changed during full clean: {path}.") from error
            if not stat.S_ISDIR(current_metadata.st_mode) or (current_metadata.st_dev, current_metadata.st_ino) != (
                opened_metadata.st_dev,
                opened_metadata.st_ino,
            ):
                raise ValueError(f"Generated publication directory changed during full clean: {path}.")
            os.rmdir(name, dir_fd=parent)
        finally:
            os.close(descriptor)

    def _open_parent(self, parts: tuple[str, ...], *, create: bool) -> int | None:
        self._require_open()
        descriptor = os.dup(self._descriptor)
        try:
            for part in parts:
                if create:
                    try:
                        os.mkdir(part, 0o755, dir_fd=descriptor)
                    except FileExistsError:
                        pass
                try:
                    next_descriptor = os.open(part, _DIRECTORY_FLAGS, dir_fd=descriptor)
                except FileNotFoundError:
                    os.close(descriptor)
                    return None
                except OSError as error:
                    raise ValueError(f"Generated publication path crosses a symlink or non-directory below {self.requested_path}: {part}.") from error
                os.close(descriptor)
                descriptor = next_descriptor
        except BaseException:
            try:
                os.close(descriptor)
            except OSError:
                pass
            raise
        return descriptor

    def _write(
        self,
        parent: int,
        name: str,
        *,
        payload: bytes | None = None,
        source: BinaryIO | None = None,
        mode: int,
        replace: bool,
    ) -> None:
        temp_name = f".{name}.paradev-{uuid4().hex}.tmp"
        descriptor: int | None = None
        try:
            descriptor = os.open(
                temp_name,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0),
                0o600,
                dir_fd=parent,
            )
            if payload is not None:
                _write_all(descriptor, payload)
            elif source is not None:
                while chunk := source.read(1024 * 1024):
                    _write_all(descriptor, chunk)
            else:
                raise AssertionError("Publication write requires bytes or a staged source.")
            os.fchmod(descriptor, mode)
            os.fsync(descriptor)
            os.close(descriptor)
            descriptor = None
            if replace:
                os.rename(temp_name, name, src_dir_fd=parent, dst_dir_fd=parent)
            else:
                os.link(
                    temp_name,
                    name,
                    src_dir_fd=parent,
                    dst_dir_fd=parent,
                    follow_symlinks=False,
                )
                os.unlink(temp_name, dir_fd=parent)
            _fsync(parent)
        except BaseException:
            if descriptor is not None:
                os.close(descriptor)
            try:
                os.unlink(temp_name, dir_fd=parent)
            except FileNotFoundError:
                pass
            raise

    def _require_open(self) -> None:
        if self._descriptor < 0:
            raise ValueError("Generated publication directory is already closed.")


@contextmanager
def open_anchored_directory(
    path: Path,
    *,
    create: bool = True,
) -> Iterator[AnchoredDirectory]:
    """Retain one descriptor-anchored generated-directory authority."""

    if _is_windows_platform():
        with _open_windows_anchored_directory(path, create=create) as authority:
            yield authority
        return
    if not _ANCHORED_PUBLICATION_SUPPORTED:
        raise ValueError("Safe descriptor-anchored generated publication is unavailable on this platform.")
    requested = path.expanduser()
    absolute = Path(os.path.abspath(requested))
    try:
        descriptor = _open_directory_path(absolute, create=create)
    except FileNotFoundError:
        if not create:
            raise
        raise
    except OSError as error:
        raise ValueError(f"Generated publication root crosses a symlink or non-directory: {requested}.") from error
    authority = AnchoredDirectory(requested, absolute, descriptor)
    try:
        yield authority
        authority.verify_path()
    finally:
        authority.close()


def _is_windows_platform() -> bool:
    """Return whether publication should use the retained Win32 backend."""

    return os.name == "nt"


def _open_windows_anchored_directory(
    path: Path,
    *,
    create: bool,
) -> ContextManager[AnchoredDirectory]:
    """Load the Win32 adapter lazily so POSIX import behavior stays unchanged."""

    from ._fs_windows import open_windows_anchored_directory

    return open_windows_anchored_directory(path, create=create)


def _open_directory_path(path: Path, *, create: bool) -> int:
    absolute = Path(os.path.abspath(path))
    descriptor = os.open(absolute.anchor, _DIRECTORY_FLAGS)
    try:
        for part in absolute.parts[1:]:
            if create:
                try:
                    os.mkdir(part, 0o755, dir_fd=descriptor)
                except FileExistsError:
                    pass
            next_descriptor = os.open(part, _DIRECTORY_FLAGS, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = next_descriptor
    except BaseException:
        os.close(descriptor)
        raise
    return descriptor


def _relative_parts(value: str | PurePosixPath) -> tuple[str, ...]:
    text = str(value).replace("\\", "/")
    path = PurePosixPath(text)
    if not text or text != path.as_posix() or path.is_absolute() or text == "." or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError(f"Generated publication path must be a normalized relative path: {value!r}.")
    return path.parts


def _path_part_identity(value: str) -> str:
    return unicodedata.normalize("NFC", value).casefold()


def _open_verified_regular_file(
    path: Path,
    *,
    expected: os.stat_result,
    label: str,
) -> int:
    try:
        descriptor = os.open(
            path,
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_CLOEXEC", 0),
        )
    except OSError as error:
        raise ValueError(label) from error
    opened = os.fstat(descriptor)
    if not stat.S_ISREG(opened.st_mode) or (opened.st_dev, opened.st_ino) != (
        expected.st_dev,
        expected.st_ino,
    ):
        os.close(descriptor)
        raise ValueError(label)
    return descriptor


def _linux_mount_table() -> tuple[tuple[int, str], ...]:
    if not sys.platform.startswith("linux"):
        return ()
    try:
        rows = Path("/proc/self/mountinfo").read_text(encoding="utf-8").splitlines()
    except OSError:
        return ()
    mounts: list[tuple[int, str]] = []
    for row in rows:
        fields = row.split()
        if len(fields) < 6:
            continue
        try:
            mount_id = int(fields[0])
        except ValueError:
            continue
        mount_point = fields[4]
        for encoded, decoded in (
            ("\\040", " "),
            ("\\011", "\t"),
            ("\\012", "\n"),
            ("\\134", "\\"),
        ):
            mount_point = mount_point.replace(encoded, decoded)
        mounts.append((mount_id, mount_point))
    return tuple(sorted(mounts, key=lambda item: len(item[1]), reverse=True))


def _descriptor_mount_id(
    descriptor: int,
    mount_table: tuple[tuple[int, str], ...],
) -> int | None:
    if not mount_table:
        return None
    try:
        path = os.readlink(f"/proc/self/fd/{descriptor}")
    except OSError:
        return None
    if path.endswith(" (deleted)"):
        path = path.removesuffix(" (deleted)")
    for mount_id, mount_point in mount_table:
        if path == mount_point or path.startswith(f"{mount_point.rstrip('/')}/"):
            return mount_id
    return None


def _write_all(descriptor: int, payload: bytes) -> None:
    view = memoryview(payload)
    while view:
        written = os.write(descriptor, view)
        if written <= 0:
            raise OSError("Generated publication write made no forward progress.")
        view = view[written:]


def _fsync(descriptor: int) -> None:
    try:
        os.fsync(descriptor)
    except OSError as error:
        unsupported = {
            errno.EINVAL,
            errno.ENOTSUP,
            getattr(errno, "EOPNOTSUPP", errno.ENOTSUP),
        }
        if error.errno not in unsupported:
            raise
