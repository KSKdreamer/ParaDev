"""Contracts for retained Win32 module-directory authoring transactions."""

from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from paradev._win32_fs import (
    Win32FileGuard,
    Win32FileMetadata,
    Win32FileSnapshot,
    Win32FilesystemUnavailable,
)
from paradev.sdk._module_fs_windows import (
    WindowsModuleMutationUnavailable,
    WindowsScaffoldRollbackIncomplete,
    cleanup_module_quarantine_windows,
    remove_module_directory_windows,
    rename_module_directory_windows,
    write_scaffold_batch_windows,
    write_scaffold_files_windows,
)

_DIRECTORY_ATTRIBUTE = 0x10


@dataclass(slots=True)
class _FakeEntry:
    """One in-memory retained filesystem entry."""

    file_id: int
    directory: bool
    mtime_ns: int
    content: bytes = b""
    children: dict[str, "_FakeEntry"] = field(default_factory=dict)


class _FakeAuthority:
    """Small exact-semantics fake for the private Win32 authority boundary."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._clock = 1
        self._next_id = 2
        self._root = _FakeEntry(
            file_id=1,
            directory=True,
            mtime_ns=self._tick(),
        )
        self.identity = self._metadata(self._root).identity
        self.closed = False
        self.verified = 0
        self.move_log: list[tuple[tuple[str, ...], tuple[str, ...]]] = []
        self.before_move: (
            Callable[
                [
                    "_FakeAuthority",
                    tuple[str, ...],
                    tuple[str, ...],
                ],
                None,
            ]
            | None
        ) = None
        self.before_remove_file: (
            Callable[
                ["_FakeAuthority", tuple[str, ...]],
                None,
            ]
            | None
        ) = None

    def close(self) -> None:
        self.closed = True

    def verify_path(self) -> None:
        self.verified += 1

    def directory_names(
        self,
        parts: tuple[str, ...] = (),
    ) -> tuple[str, ...]:
        entry = self._lookup(parts)
        if not entry.directory:
            raise NotADirectoryError("/".join(parts))
        return tuple(sorted(entry.children))

    def create_directory(
        self,
        parts: tuple[str, ...],
        *,
        exist_ok: bool = False,
    ) -> tuple[Win32FileMetadata, bool]:
        parent, name = self._parent(parts)
        existing = parent.children.get(name)
        if existing is not None:
            if not exist_ok:
                raise FileExistsError("/".join(parts))
            if not existing.directory:
                raise NotADirectoryError("/".join(parts))
            return self._metadata(existing), False
        entry = self._new_entry(directory=True)
        parent.children[name] = entry
        self._touch(parent)
        return self._metadata(entry), True

    def guarded_move_entry(
        self,
        source_parts: tuple[str, ...],
        target_parts: tuple[str, ...],
        *,
        guard: Win32FileGuard,
        create_target_parent: bool = False,
        expected_target_parent_identity: tuple[int, int] | None = None,
    ) -> Win32FileSnapshot:
        source_parent, source_name = self._parent(source_parts)
        source = source_parent.children.get(source_name)
        if source is None:
            raise FileNotFoundError("/".join(source_parts))
        snapshot = self._snapshot(source)
        guard(self._metadata(source_parent).identity, snapshot)
        if self.before_move is not None:
            self.before_move(self, source_parts, target_parts)
        if create_target_parent:
            self._create_parent_chain(target_parts[:-1])
        target_parent, target_name = self._parent(target_parts)
        if expected_target_parent_identity is not None and self._metadata(target_parent).identity != expected_target_parent_identity:
            raise OSError("fake retained target parent changed before move")
        if target_name in target_parent.children:
            raise FileExistsError("/".join(target_parts))
        del source_parent.children[source_name]
        target_parent.children[target_name] = source
        self._touch(source_parent)
        self._touch(target_parent)
        self.move_log.append((source_parts, target_parts))
        return snapshot

    def remove_empty_directory(
        self,
        parts: tuple[str, ...],
        *,
        expected_identity: tuple[int, int],
    ) -> bool:
        try:
            parent, name = self._parent(parts)
        except FileNotFoundError:
            return False
        entry = parent.children.get(name)
        if entry is None:
            return False
        if not entry.directory or self._metadata(entry).identity != expected_identity or entry.children:
            return False
        del parent.children[name]
        self._touch(parent)
        return True

    def remove_directory_tree(
        self,
        parts: tuple[str, ...],
        *,
        expected_identity: tuple[int, int],
    ) -> bool:
        try:
            parent, name = self._parent(parts)
        except FileNotFoundError:
            return False
        entry = parent.children.get(name)
        if entry is None:
            return False
        if not entry.directory or self._metadata(entry).identity != expected_identity:
            return False
        del parent.children[name]
        self._touch(parent)
        return True

    def read_file_snapshot(
        self,
        parts: tuple[str, ...],
        *,
        max_bytes: int | None = None,
    ) -> Win32FileSnapshot | None:
        try:
            entry = self._lookup(parts)
        except FileNotFoundError:
            return None
        if not entry.directory and max_bytes is not None and len(entry.content) > max_bytes:
            raise ValueError("fake retained file is too large")
        return self._snapshot(entry)

    def entry_metadata(
        self,
        parts: tuple[str, ...],
    ) -> Win32FileMetadata | None:
        try:
            return self._metadata(self._lookup(parts))
        except FileNotFoundError:
            return None

    def write_bytes_snapshot(
        self,
        parts: tuple[str, ...],
        payload: bytes,
        *,
        replace: bool,
        create_parent: bool = False,
    ) -> tuple[tuple[int, int], Win32FileSnapshot]:
        if create_parent:
            self._create_parent_chain(parts[:-1])
        parent, name = self._parent(parts)
        if name in parent.children and not replace:
            raise FileExistsError("/".join(parts))
        entry = self._new_entry(directory=False, content=payload)
        parent.children[name] = entry
        self._touch(parent)
        return self._metadata(parent).identity, self._snapshot(entry)

    def guarded_remove_file(
        self,
        parts: tuple[str, ...],
        *,
        guard: Win32FileGuard,
        missing_ok: bool = False,
    ) -> tuple[tuple[int, int], Win32FileSnapshot | None]:
        if self.before_remove_file is not None:
            self.before_remove_file(self, parts)
        try:
            parent, name = self._parent(parts)
        except FileNotFoundError:
            guard(self.identity, None)
            if missing_ok:
                return self.identity, None
            raise
        entry = parent.children.get(name)
        parent_identity = self._metadata(parent).identity
        if entry is None:
            guard(parent_identity, None)
            if missing_ok:
                return parent_identity, None
            raise FileNotFoundError("/".join(parts))
        if entry.directory:
            raise IsADirectoryError("/".join(parts))
        snapshot = self._snapshot(entry)
        guard(parent_identity, snapshot)
        del parent.children[name]
        self._touch(parent)
        return parent_identity, snapshot

    def seed_directory(self, parts: tuple[str, ...]) -> None:
        self._create_parent_chain(parts)

    def seed_file(self, parts: tuple[str, ...], content: bytes) -> None:
        self._create_parent_chain(parts[:-1])
        parent, name = self._parent(parts)
        parent.children[name] = self._new_entry(
            directory=False,
            content=content,
        )
        self._touch(parent)

    def read_bytes(self, parts: tuple[str, ...]) -> bytes:
        snapshot = self.read_file_snapshot(parts)
        if snapshot is None or snapshot.content is None:
            raise FileNotFoundError("/".join(parts))
        return snapshot.content

    def exists(self, parts: tuple[str, ...]) -> bool:
        return self.entry_metadata(parts) is not None

    def _create_parent_chain(self, parts: tuple[str, ...]) -> None:
        current = self._root
        for part in parts:
            child = current.children.get(part)
            if child is None:
                child = self._new_entry(directory=True)
                current.children[part] = child
                self._touch(current)
            if not child.directory:
                raise NotADirectoryError("/".join(parts))
            current = child

    def _lookup(self, parts: tuple[str, ...]) -> _FakeEntry:
        current = self._root
        for part in parts:
            if not current.directory:
                raise NotADirectoryError("/".join(parts))
            try:
                current = current.children[part]
            except KeyError as error:
                raise FileNotFoundError("/".join(parts)) from error
        return current

    def _parent(
        self,
        parts: tuple[str, ...],
    ) -> tuple[_FakeEntry, str]:
        if not parts:
            raise ValueError("fake root has no parent")
        parent = self._lookup(parts[:-1])
        if not parent.directory:
            raise NotADirectoryError("/".join(parts[:-1]))
        return parent, parts[-1]

    def _new_entry(
        self,
        *,
        directory: bool,
        content: bytes = b"",
    ) -> _FakeEntry:
        entry = _FakeEntry(
            file_id=self._next_id,
            directory=directory,
            mtime_ns=self._tick(),
            content=content,
        )
        self._next_id += 1
        return entry

    def _metadata(
        self,
        entry: _FakeEntry,
        *,
        include_mtime: bool = False,
    ) -> Win32FileMetadata:
        return Win32FileMetadata(
            volume_serial=11,
            file_id=entry.file_id,
            attributes=_DIRECTORY_ATTRIBUTE if entry.directory else 0,
            size=0 if entry.directory else len(entry.content),
            mtime_ns=entry.mtime_ns if include_mtime else 0,
        )

    def _snapshot(self, entry: _FakeEntry) -> Win32FileSnapshot:
        return Win32FileSnapshot(
            metadata=self._metadata(entry, include_mtime=True),
            content=None if entry.directory else entry.content,
        )

    def _touch(self, entry: _FakeEntry) -> None:
        entry.mtime_ns = self._tick()

    def _tick(self) -> int:
        self._clock += 1
        return self._clock


def _project_paths(tmp_path: Path) -> tuple[Path, Path]:
    project_root = tmp_path / "project"
    return project_root, project_root / "src"


def _authority(
    source_root: Path,
    *,
    family: str = "idea",
) -> _FakeAuthority:
    authority = _FakeAuthority(source_root)
    authority.seed_directory(("modules", family))
    return authority


def _rendered(
    title: str,
) -> list[dict[str, object]]:
    return [
        {
            "relative_module_path": "meta.yaml",
            "content": f"type: idea\ntitle: {title}",
        },
        {
            "relative_module_path": "content/def.txt",
            "content": f"ideas = {{ {title} = {{}} }}",
        },
    ]


@pytest.mark.unit
def test_windows_scaffold_installs_new_module_as_one_staged_directory(
    tmp_path: Path,
) -> None:
    project_root, source_root = _project_paths(tmp_path)
    authority = _authority(source_root)

    write_scaffold_files_windows(
        project_root,
        source_root,
        "idea",
        "ALPHA",
        "ALPHA",
        _rendered("Alpha"),
        False,
        _authority_opener=lambda _path: authority,
    )

    target = ("modules", "idea", "ALPHA")
    assert authority.read_bytes((*target, "meta.yaml")) == (b"type: idea\ntitle: Alpha\n")
    assert authority.read_bytes((*target, "content", "def.txt")) == (b"ideas = { Alpha = {} }\n")
    install_moves = [move for move in authority.move_log if move[1] == target]
    assert len(install_moves) == 1
    assert install_moves[0][0][-1] == "module.stage"
    assert authority.directory_names((".paradev", "module-transactions")) == ()
    assert authority.verified == 1
    assert authority.closed is True


@pytest.mark.unit
def test_windows_scaffold_populates_existing_empty_titled_module_without_force(
    tmp_path: Path,
) -> None:
    project_root, source_root = _project_paths(tmp_path)
    authority = _authority(source_root)
    module = ("modules", "idea", "EMPTY - Titled module")
    authority.seed_directory(module)

    write_scaffold_files_windows(
        project_root,
        source_root,
        "idea",
        "EMPTY",
        "EMPTY - Titled module",
        _rendered("Empty"),
        False,
        _authority_opener=lambda _path: authority,
    )

    assert authority.read_bytes((*module, "meta.yaml")) == (b"type: idea\ntitle: Empty\n")
    assert authority.read_bytes((*module, "content", "def.txt")) == (b"ideas = { Empty = {} }\n")


@pytest.mark.unit
def test_windows_scaffold_without_force_preserves_existing_target_file(
    tmp_path: Path,
) -> None:
    project_root, source_root = _project_paths(tmp_path)
    authority = _authority(source_root)
    module = ("modules", "idea", "EXISTING")
    authority.seed_directory(module)
    authority.seed_file((*module, "meta.yaml"), b"human-owned\n")

    with pytest.raises(FileExistsError, match="meta.yaml"):
        write_scaffold_files_windows(
            project_root,
            source_root,
            "idea",
            "EXISTING",
            "EXISTING",
            _rendered("Replacement"),
            False,
            _authority_opener=lambda _path: authority,
        )

    assert authority.read_bytes((*module, "meta.yaml")) == b"human-owned\n"
    assert not authority.exists((*module, "content"))


@pytest.mark.unit
def test_windows_scaffold_batch_rolls_back_all_installed_modules(
    tmp_path: Path,
) -> None:
    project_root, source_root = _project_paths(tmp_path)
    authority = _authority(source_root)

    def race_second_target(
        current: _FakeAuthority,
        _source: tuple[str, ...],
        target: tuple[str, ...],
    ) -> None:
        if target == ("modules", "idea", "B"):
            current.seed_directory(target)

    authority.before_move = race_second_target

    with pytest.raises(FileExistsError):
        write_scaffold_batch_windows(
            project_root,
            source_root,
            [
                ("idea", "A", "A", _rendered("A")),
                ("idea", "B", "B", _rendered("B")),
            ],
            _authority_opener=lambda _path: authority,
        )

    assert not authority.exists(("modules", "idea", "A"))
    assert authority.exists(("modules", "idea", "B"))
    assert authority.directory_names((".paradev", "module-transactions")) == ()


@pytest.mark.unit
def test_windows_scaffold_batch_rolls_back_when_validation_rejects(
    tmp_path: Path,
) -> None:
    project_root, source_root = _project_paths(tmp_path)
    authority = _authority(source_root)
    validated = False

    def reject_build() -> None:
        nonlocal validated
        validated = True
        assert authority.exists(("modules", "idea", "A"))
        raise RuntimeError("build rejected")

    with pytest.raises(RuntimeError, match="build rejected"):
        write_scaffold_batch_windows(
            project_root,
            source_root,
            [("idea", "A", "A", _rendered("A"))],
            validate=reject_build,
            _authority_opener=lambda _path: authority,
        )

    assert validated is True
    assert not authority.exists(("modules", "idea", "A"))
    assert authority.directory_names((".paradev", "module-transactions")) == ()


@pytest.mark.unit
def test_windows_scaffold_batch_preserves_changed_target_and_recovery(
    tmp_path: Path,
) -> None:
    project_root, source_root = _project_paths(tmp_path)
    authority = _authority(source_root)

    def change_first_before_second(
        current: _FakeAuthority,
        _source: tuple[str, ...],
        target: tuple[str, ...],
    ) -> None:
        if target == ("modules", "idea", "B"):
            current.seed_file(
                ("modules", "idea", "A", "meta.yaml"),
                b"external owner\n",
            )
            current.seed_directory(target)

    authority.before_move = change_first_before_second

    with pytest.raises(WindowsScaffoldRollbackIncomplete) as raised:
        write_scaffold_batch_windows(
            project_root,
            source_root,
            [
                ("idea", "A", "A", _rendered("A")),
                ("idea", "B", "B", _rendered("B")),
            ],
            _authority_opener=lambda _path: authority,
        )

    assert authority.read_bytes(("modules", "idea", "A", "meta.yaml")) == b"external owner\n"
    recovery_parts = raised.value.recovery_path.relative_to(source_root).parts
    assert authority.exists(recovery_parts)


@pytest.mark.unit
def test_windows_scaffold_refuses_replaced_target_parent_without_redirect(
    tmp_path: Path,
) -> None:
    project_root, source_root = _project_paths(tmp_path)
    authority = _authority(source_root)
    authority.seed_file(
        ("modules", "idea", "protected.txt"),
        b"human source\n",
    )

    def replace_family_before_move(
        current: _FakeAuthority,
        _source: tuple[str, ...],
        target: tuple[str, ...],
    ) -> None:
        if target != ("modules", "idea", "SAFE"):
            return
        modules = current._lookup(("modules",))
        original = modules.children.pop("idea")
        modules.children["idea-displaced"] = original
        modules.children["idea"] = current._new_entry(directory=True)
        current._touch(modules)

    authority.before_move = replace_family_before_move

    with pytest.raises(OSError, match="target parent changed"):
        write_scaffold_files_windows(
            project_root,
            source_root,
            "idea",
            "SAFE",
            "SAFE",
            _rendered("Safe"),
            False,
            _authority_opener=lambda _path: authority,
        )

    assert not authority.exists(("modules", "idea", "SAFE"))
    assert authority.read_bytes(("modules", "idea-displaced", "protected.txt")) == b"human source\n"


@pytest.mark.unit
def test_windows_force_scaffold_restores_originals_after_install_error(
    tmp_path: Path,
) -> None:
    project_root, source_root = _project_paths(tmp_path)
    authority = _authority(source_root)
    module = ("modules", "idea", "EXISTING")
    authority.seed_directory(module)
    authority.seed_file((*module, "meta.yaml"), b"original meta\n")
    authority.seed_file(
        (*module, "content", "def.txt"),
        b"original def\n",
    )

    def fail_second_backup(
        _current: _FakeAuthority,
        source: tuple[str, ...],
        target: tuple[str, ...],
    ) -> None:
        if source == (*module, "content", "def.txt") and target[-1].endswith(".backup"):
            raise OSError("injected second backup failure")

    authority.before_move = fail_second_backup

    with pytest.raises(OSError, match="injected second backup failure"):
        write_scaffold_files_windows(
            project_root,
            source_root,
            "idea",
            "EXISTING",
            "EXISTING",
            _rendered("Replacement"),
            True,
            _authority_opener=lambda _path: authority,
        )

    assert authority.read_bytes((*module, "meta.yaml")) == b"original meta\n"
    assert authority.read_bytes((*module, "content", "def.txt")) == b"original def\n"
    assert authority.directory_names((".paradev", "module-transactions")) == ()


@pytest.mark.unit
def test_windows_force_scaffold_never_removes_changed_rollback_target(
    tmp_path: Path,
) -> None:
    project_root, source_root = _project_paths(tmp_path)
    authority = _authority(source_root)
    module = ("modules", "idea", "EXISTING")
    authority.seed_directory(module)
    authority.seed_file((*module, "meta.yaml"), b"original meta\n")
    authority.seed_file(
        (*module, "content", "def.txt"),
        b"original def\n",
    )

    def change_first_then_fail(
        current: _FakeAuthority,
        source: tuple[str, ...],
        target: tuple[str, ...],
    ) -> None:
        if source == (*module, "content", "def.txt") and target[-1].endswith(".backup"):
            current.seed_file(
                (*module, "meta.yaml"),
                b"external edit\n",
            )
            raise OSError("injected second backup failure")

    authority.before_move = change_first_then_fail

    with pytest.raises(WindowsScaffoldRollbackIncomplete) as raised:
        write_scaffold_files_windows(
            project_root,
            source_root,
            "idea",
            "EXISTING",
            "EXISTING",
            _rendered("Replacement"),
            True,
            _authority_opener=lambda _path: authority,
        )

    assert authority.read_bytes((*module, "meta.yaml")) == b"external edit\n"
    recovery_parts = raised.value.recovery_path.relative_to(source_root).parts
    assert authority.exists(recovery_parts)


@pytest.mark.unit
def test_windows_force_scaffold_binds_existing_module_root_identity(
    tmp_path: Path,
) -> None:
    project_root, source_root = _project_paths(tmp_path)
    authority = _authority(source_root)
    module = ("modules", "idea", "EXISTING")
    authority.seed_directory(module)
    authority.seed_file((*module, "meta.yaml"), b"original meta\n")
    authority.seed_file((*module, "protected.txt"), b"human source\n")

    def replace_module_before_first_backup(
        current: _FakeAuthority,
        source: tuple[str, ...],
        target: tuple[str, ...],
    ) -> None:
        if source != (*module, "meta.yaml") or not target[-1].endswith(".backup"):
            return
        family = current._lookup(("modules", "idea"))
        original = family.children.pop("EXISTING")
        family.children["EXISTING-displaced"] = original
        family.children["EXISTING"] = current._new_entry(directory=True)
        current._touch(family)

    authority.before_move = replace_module_before_first_backup

    with pytest.raises(WindowsScaffoldRollbackIncomplete) as raised:
        write_scaffold_files_windows(
            project_root,
            source_root,
            "idea",
            "EXISTING",
            "EXISTING",
            _rendered("Replacement"),
            True,
            _authority_opener=lambda _path: authority,
        )

    assert not authority.exists((*module, "meta.yaml"))
    assert authority.read_bytes(("modules", "idea", "EXISTING-displaced", "protected.txt")) == b"human source\n"
    recovery_parts = raised.value.recovery_path.relative_to(source_root).parts
    assert authority.read_bytes((*recovery_parts, "000000.backup")) == b"original meta\n"


@pytest.mark.unit
def test_windows_module_rename_uses_exact_alias_and_no_clobber_guards(
    tmp_path: Path,
) -> None:
    _project_root, source_root = _project_paths(tmp_path)
    authority = _authority(source_root)
    authority.seed_directory(("modules", "idea", "OLD - Title"))
    authority.seed_file(
        ("modules", "idea", "OLD - Title", "meta.yaml"),
        b"type: idea\n",
    )

    rename_module_directory_windows(
        source_root,
        "idea",
        "OLD - Title",
        "NEW - Title",
        "NEW",
        _authority_opener=lambda _path: authority,
    )

    assert not authority.exists(("modules", "idea", "OLD - Title"))
    assert authority.read_bytes(("modules", "idea", "NEW - Title", "meta.yaml")) == b"type: idea\n"

    authority.closed = False
    authority.seed_directory(("modules", "idea", "new - Other"))
    with pytest.raises(OSError, match="conflicting physical folder"):
        rename_module_directory_windows(
            source_root,
            "idea",
            "NEW - Title",
            "THIRD",
            "NEW",
            _authority_opener=lambda _path: authority,
        )


@pytest.mark.unit
def test_windows_module_rename_allows_case_only_same_identity_target(
    tmp_path: Path,
) -> None:
    _project_root, source_root = _project_paths(tmp_path)
    authority = _authority(source_root)
    authority.seed_directory(("modules", "idea", "mixed"))

    rename_module_directory_windows(
        source_root,
        "idea",
        "mixed",
        "MIXED",
        "MIXED",
        _authority_opener=lambda _path: authority,
    )

    assert not authority.exists(("modules", "idea", "mixed"))
    assert authority.exists(("modules", "idea", "MIXED"))


@pytest.mark.unit
def test_windows_registry_rename_supports_collection_container(
    tmp_path: Path,
) -> None:
    _project_root, source_root = _project_paths(tmp_path)
    authority = _authority(source_root)
    authority.seed_directory(("collections", "focus", "OLD - Tree"))
    authority.seed_file(
        ("collections", "focus", "OLD - Tree", "meta.yaml"),
        b"title: Tree\n",
    )

    rename_module_directory_windows(
        source_root,
        "focus",
        "OLD - Tree",
        "NEW",
        "NEW",
        container="collections",
        _authority_opener=lambda _path: authority,
    )

    assert not authority.exists(("collections", "focus", "OLD - Tree"))
    assert authority.read_bytes(("collections", "focus", "NEW", "meta.yaml")) == (b"title: Tree\n")


@pytest.mark.unit
def test_windows_module_quarantine_cleanup_deletes_only_unchanged_tree(
    tmp_path: Path,
) -> None:
    _project_root, source_root = _project_paths(tmp_path)
    authority = _authority(source_root)
    module = ("modules", "idea", "REMOVE")
    authority.seed_directory(module)
    authority.seed_file((*module, "meta.yaml"), b"type: idea\n")

    name, path = remove_module_directory_windows(
        source_root,
        "idea",
        "REMOVE",
        _authority_opener=lambda _path: authority,
    )
    authority.closed = False
    pending, error = cleanup_module_quarantine_windows(
        source_root,
        name,
        path,
        _authority_opener=lambda _path: authority,
    )

    assert pending is None
    assert error == ""
    assert not authority.exists((".paradev", "module-trash", name))


@pytest.mark.unit
def test_windows_module_quarantine_cleanup_preserves_changed_tree(
    tmp_path: Path,
) -> None:
    _project_root, source_root = _project_paths(tmp_path)
    authority = _authority(source_root)
    module = ("modules", "idea", "REMOVE")
    authority.seed_directory(module)
    authority.seed_file((*module, "meta.yaml"), b"type: idea\n")

    name, path = remove_module_directory_windows(
        source_root,
        "idea",
        "REMOVE",
        _authority_opener=lambda _path: authority,
    )
    authority.seed_file(
        (".paradev", "module-trash", name, "meta.yaml"),
        b"changed after removal\n",
    )
    authority.closed = False
    pending, error = cleanup_module_quarantine_windows(
        source_root,
        name,
        path,
        _authority_opener=lambda _path: authority,
    )

    assert pending == path
    assert "contents changed" in error
    assert authority.read_bytes((".paradev", "module-trash", name, "meta.yaml")) == b"changed after removal\n"


@pytest.mark.unit
def test_windows_module_quarantine_cleanup_preserves_mid_cleanup_edit(
    tmp_path: Path,
) -> None:
    _project_root, source_root = _project_paths(tmp_path)
    authority = _authority(source_root)
    module = ("modules", "idea", "REMOVE")
    authority.seed_directory(module)
    authority.seed_file((*module, "meta.yaml"), b"type: idea\n")

    name, path = remove_module_directory_windows(
        source_root,
        "idea",
        "REMOVE",
        _authority_opener=lambda _path: authority,
    )
    quarantine_file = (
        ".paradev",
        "module-trash",
        name,
        "meta.yaml",
    )
    injected = False

    def change_before_guarded_delete(
        current: _FakeAuthority,
        parts: tuple[str, ...],
    ) -> None:
        nonlocal injected
        if not injected and parts == quarantine_file:
            injected = True
            current.seed_file(parts, b"concurrent recovery edit\n")

    authority.before_remove_file = change_before_guarded_delete
    authority.closed = False
    pending, error = cleanup_module_quarantine_windows(
        source_root,
        name,
        path,
        _authority_opener=lambda _path: authority,
    )

    assert injected is True
    assert pending == path
    assert "changed before mutation" in error
    assert authority.read_bytes(quarantine_file) == (b"concurrent recovery edit\n")


@pytest.mark.unit
def test_windows_module_adapter_maps_unavailable_authority_before_mutation(
    tmp_path: Path,
) -> None:
    project_root, source_root = _project_paths(tmp_path)

    def unavailable(_path: Path) -> _FakeAuthority:
        raise Win32FilesystemUnavailable("fixed NTFS/ReFS volume required")

    with pytest.raises(
        WindowsModuleMutationUnavailable,
        match="fixed NTFS/ReFS volume required",
    ):
        write_scaffold_files_windows(
            project_root,
            source_root,
            "idea",
            "SAFE",
            "SAFE",
            _rendered("Safe"),
            False,
            _authority_opener=unavailable,
        )


@pytest.mark.unit
def test_windows_module_adapter_rejects_non_nfc_components(
    tmp_path: Path,
) -> None:
    project_root, source_root = _project_paths(tmp_path)
    authority = _authority(source_root)

    with pytest.raises(ValueError, match="NFC spelling"):
        write_scaffold_files_windows(
            project_root,
            source_root,
            "idea",
            "Cafe\u0301",
            "Cafe\u0301",
            _rendered("Cafe"),
            False,
            _authority_opener=lambda _path: authority,
        )


@pytest.mark.unit
def test_windows_module_adapter_encodes_scaffold_content_strictly(
    tmp_path: Path,
) -> None:
    project_root, source_root = _project_paths(tmp_path)
    authority = _authority(source_root)
    rendered = [
        {
            "relative_module_path": "meta.yaml",
            "content": "invalid surrogate: \ud800",
        }
    ]

    with pytest.raises(UnicodeEncodeError):
        write_scaffold_files_windows(
            project_root,
            source_root,
            "idea",
            "STRICT",
            "STRICT",
            rendered,
            False,
            _authority_opener=lambda _path: authority,
        )

    assert not authority.exists(("modules", "idea", "STRICT"))


@pytest.mark.unit
def test_windows_module_removal_maps_unsafe_preflight_without_unbound_state(
    tmp_path: Path,
) -> None:
    _project_root, source_root = _project_paths(tmp_path)
    authority = _authority(source_root)
    authority.seed_directory(("modules", "idea", "REMOVE"))

    def unsafe_names(_parts: tuple[str, ...] = ()) -> tuple[str, ...]:
        raise Win32FilesystemUnavailable("retained preflight unavailable")

    authority.directory_names = unsafe_names  # type: ignore[method-assign]

    with pytest.raises(
        WindowsModuleMutationUnavailable,
        match="retained preflight unavailable",
    ):
        remove_module_directory_windows(
            source_root,
            "idea",
            "REMOVE",
            _authority_opener=lambda _path: authority,
        )


@pytest.mark.skipif(
    os.name != "nt",
    reason="Requires native retained Win32 directory mutation semantics.",
)
def test_windows_module_adapter_native_single_scaffold(
    tmp_path: Path,
) -> None:
    project_root = tmp_path / "project"
    source_root = project_root / "src"
    (source_root / "modules" / "idea").mkdir(parents=True)

    write_scaffold_files_windows(
        project_root,
        source_root,
        "idea",
        "NATIVE",
        "NATIVE",
        _rendered("Native"),
        False,
    )

    assert (source_root / "modules" / "idea" / "NATIVE" / "meta.yaml").read_bytes() == b"type: idea\ntitle: Native\n"
