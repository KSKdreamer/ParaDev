"""Win32 adapter for the generated-publication filesystem contract."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path, PurePosixPath
from typing import Iterator

from paradev._win32_fs import Win32DirectoryAuthority, Win32UnsafePathError
from paradev.portable_paths import windows_portable_component_error

from ._fs import AnchoredDirectory, _path_part_identity, _relative_parts


class WindowsAnchoredDirectory(AnchoredDirectory):
    """Generated-publication authority backed by retained Win32 handles."""

    def __init__(self, authority: Win32DirectoryAuthority) -> None:
        self.requested_path = authority.requested_path
        self.path = authority.path
        self._descriptor = -1
        self._identity = authority.identity
        self._authority: Win32DirectoryAuthority | None = authority

    def close(self) -> None:
        """Close every retained Win32 handle."""

        if self._authority is None:
            return
        self._authority.close()
        self._authority = None

    def is_empty(self) -> bool:
        """Return whether the retained directory contains no entries."""

        return self._require_windows_authority().is_empty()

    def entry_exists(self, relative_path: str | PurePosixPath) -> bool:
        """Check for an existing safe entry without following reparse points."""

        return self._require_windows_authority().entry_exists(_windows_relative_parts(relative_path))

    def same_entry(
        self,
        left_path: str | PurePosixPath,
        right_path: str | PurePosixPath,
    ) -> bool:
        """Return whether two names identify the same regular file."""

        return self._require_windows_authority().same_regular_entry(
            _windows_relative_parts(left_path),
            _windows_relative_parts(right_path),
        )

    def verify_path(self) -> None:
        """Reject a publication root whose lexical path changed."""

        try:
            self._require_windows_authority().verify_path()
        except (OSError, Win32UnsafePathError) as error:
            raise ValueError(f"Generated publication root changed during the build: {self.requested_path}.") from error

    def read_bytes(self, relative_path: str | PurePosixPath) -> bytes | None:
        """Read one regular generated file without following reparse points."""

        parts = _windows_relative_parts(relative_path)
        try:
            return self._require_windows_authority().read_bytes(parts)
        except Win32UnsafePathError as error:
            raise ValueError(f"Generated publication path crosses a reparse point or non-directory: {self.path.joinpath(*parts)}.") from error

    def file_matches(
        self,
        relative_path: str | PurePosixPath,
        source: Path,
    ) -> bool | None:
        """Compare one generated file with a staged regular file."""

        parts = _windows_relative_parts(relative_path)
        try:
            return self._require_windows_authority().file_matches(parts, source)
        except Win32UnsafePathError as error:
            raise ValueError(f"Generated publication file changed or crosses a reparse point: {self.path.joinpath(*parts)}.") from error

    def file_sha256_matches(
        self,
        relative_path: str | PurePosixPath,
        expected_sha256: str,
    ) -> bool | None:
        """Compare one generated file with an exact SHA-256 digest."""

        parts = _windows_relative_parts(relative_path)
        try:
            return self._require_windows_authority().file_sha256_matches(
                parts,
                expected_sha256,
            )
        except Win32UnsafePathError as error:
            raise ValueError("Generated publication file changed or crosses a reparse point: " f"{self.path.joinpath(*parts)}.") from error

    def write_bytes(
        self,
        relative_path: str | PurePosixPath,
        payload: bytes,
        *,
        mode: int = 0o644,
        replace: bool = True,
    ) -> Path:
        """Atomically publish bytes relative to the retained root."""

        del mode
        parts = _windows_relative_parts(relative_path)
        try:
            self._require_windows_authority().write_bytes(parts, payload, replace=replace)
        except Win32UnsafePathError as error:
            raise ValueError(f"Generated publication path crosses a reparse point or non-directory: {self.path.joinpath(*parts)}.") from error
        return self.requested_path.joinpath(*parts)

    def publish_file(
        self,
        relative_path: str | PurePosixPath,
        source: Path,
        *,
        replace: bool = True,
    ) -> Path:
        """Atomically publish one staged regular file."""

        parts = _windows_relative_parts(relative_path)
        try:
            self._require_windows_authority().publish_file(parts, source, replace=replace)
        except Win32UnsafePathError as error:
            raise ValueError(f"Generated publication path crosses a reparse point or non-directory: {self.path.joinpath(*parts)}.") from error
        return self.requested_path.joinpath(*parts)

    def normalize_path_spelling(
        self,
        previous_path: str | PurePosixPath,
        current_path: str | PurePosixPath,
    ) -> bool:
        """Normalize every case-aliased component to tracked spelling."""

        previous_parts = _windows_relative_parts(previous_path)
        current_parts = _windows_relative_parts(current_path)
        if len(previous_parts) != len(current_parts) or tuple(_path_part_identity(part) for part in previous_parts) != tuple(
            _path_part_identity(part) for part in current_parts
        ):
            raise ValueError(f"Generated publication spelling transition must preserve path identity: {previous_path!s} -> {current_path!s}.")
        try:
            return self._require_windows_authority().normalize_path_spelling(previous_parts, current_parts)
        except Win32UnsafePathError as error:
            raise ValueError(
                "Generated publication path crosses a reparse point or non-directory while normalizing tracked spelling: "
                f"{self.requested_path / PurePosixPath(*current_parts)}."
            ) from error

    def delete_file(
        self,
        relative_path: str | PurePosixPath,
        *,
        exact_spelling: bool = False,
        prune_empty_parents: bool = True,
    ) -> bool:
        """Delete one regular generated file and optionally prune empty parents."""

        parts = _windows_relative_parts(relative_path)
        try:
            return self._require_windows_authority().delete_file(
                parts,
                exact_spelling=exact_spelling,
                prune_empty_parents=prune_empty_parents,
            )
        except Win32UnsafePathError as error:
            raise ValueError(f"Generated publication path crosses a reparse point or changed parent: {self.path.joinpath(*parts)}.") from error

    def clear(self) -> None:
        """Remove all safe entries below the retained root."""

        try:
            self._require_windows_authority().clear()
        except Win32UnsafePathError as error:
            raise ValueError(f"Generated publication full clean crossed a reparse point or filesystem boundary: {self.requested_path}.") from error

    def _require_windows_authority(self) -> Win32DirectoryAuthority:
        if self._authority is None:
            raise ValueError("Generated publication directory is already closed.")
        return self._authority


@contextmanager
def open_windows_anchored_directory(
    path: Path,
    *,
    create: bool = True,
) -> Iterator[AnchoredDirectory]:
    """Open a retained Win32 authority through the build filesystem API."""

    try:
        authority = Win32DirectoryAuthority.open(path, create=create)
    except FileNotFoundError:
        raise
    except Win32UnsafePathError as error:
        raise ValueError(f"Generated publication root crosses a reparse point or non-directory: {path}.") from error
    except OSError as error:
        raise ValueError(f"Generated publication root cannot be retained safely: {path}. {error}") from error

    adapted = WindowsAnchoredDirectory(authority)
    try:
        yield adapted
        adapted.verify_path()
    finally:
        adapted.close()


def _windows_relative_parts(value: str | PurePosixPath) -> tuple[str, ...]:
    """Validate a normalized relative path against Win32 component rules."""

    parts = _relative_parts(value)
    for component in parts:
        if error := windows_portable_component_error(component):
            raise ValueError(f"Generated publication path component {component!r} is not portable to Windows because it {error}: {value!s}.")
    return parts
