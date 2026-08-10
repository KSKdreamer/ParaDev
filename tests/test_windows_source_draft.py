"""Contracts for retained Win32 source-draft transactions."""

from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest

from paradev._win32_fs import Win32FileMetadata, Win32FileSnapshot, Win32UnsafePathError
from paradev.sdk import Project
from paradev.sdk import project as project_sdk


def _metadata(
    *,
    file_id: int,
    content: bytes,
    mtime_ns: int,
) -> Win32FileMetadata:
    return Win32FileMetadata(
        volume_serial=11,
        file_id=file_id,
        attributes=0,
        size=len(content),
        mtime_ns=mtime_ns,
    )


@pytest.mark.unit
def test_win32_source_draft_root_dispatch_is_injectable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeAuthority:
        path = tmp_path
        identity = (11, 22)

    calls: list[tuple[Path, tuple[int, int] | None]] = []

    @contextmanager
    def fake_open(
        project_root: Path,
        *,
        root_identity: tuple[int, int] | None = None,
    ) -> Iterator[FakeAuthority]:
        calls.append((project_root, root_identity))
        yield FakeAuthority()

    monkeypatch.setattr(project_sdk, "_uses_win32_source_draft_authority", lambda: True)
    monkeypatch.setattr(project_sdk, "_open_win32_source_draft_authority", fake_open)

    root, identity = project_sdk._source_draft_root_identity(tmp_path)

    assert root == tmp_path
    assert identity == (11, 22)
    assert calls == [(tmp_path, None)]


@pytest.mark.unit
def test_win32_source_draft_authority_verifies_after_success(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeAuthority:
        identity = (11, 22)
        verified = 0
        closed = 0

        def verify_path(self) -> None:
            self.verified += 1

        def close(self) -> None:
            self.closed += 1

    authority = FakeAuthority()
    monkeypatch.setattr(
        project_sdk.Win32DirectoryAuthority,
        "open",
        lambda path, *, create: authority,
    )

    with project_sdk._open_win32_source_draft_authority(tmp_path, root_identity=(11, 22)) as opened:
        assert opened is authority

    assert authority.verified == 1
    assert authority.closed == 1


@pytest.mark.unit
def test_win32_source_draft_authority_rejects_root_change_after_success(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeAuthority:
        identity = (11, 22)
        closed = 0

        def verify_path(self) -> None:
            raise Win32UnsafePathError("lexical root changed")

        def close(self) -> None:
            self.closed += 1

    authority = FakeAuthority()
    monkeypatch.setattr(
        project_sdk.Win32DirectoryAuthority,
        "open",
        lambda path, *, create: authority,
    )

    with (
        pytest.raises(ValueError, match="project root changed before mutation"),
        project_sdk._open_win32_source_draft_authority(tmp_path, root_identity=(11, 22)),
    ):
        pass

    assert authority.closed == 1


@pytest.mark.unit
def test_win32_source_draft_authority_preserves_operation_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeAuthority:
        identity = (11, 22)
        verified = 0
        closed = 0

        def verify_path(self) -> None:
            self.verified += 1

        def close(self) -> None:
            self.closed += 1

    authority = FakeAuthority()
    monkeypatch.setattr(
        project_sdk.Win32DirectoryAuthority,
        "open",
        lambda path, *, create: authority,
    )
    expected = FileExistsError("concurrent source appeared")

    with (
        pytest.raises(FileExistsError) as raised,
        project_sdk._open_win32_source_draft_authority(tmp_path, root_identity=(11, 22)),
    ):
        raise expected

    assert raised.value is expected
    assert authority.verified == 0
    assert authority.closed == 1


@pytest.mark.unit
def test_win32_project_source_snapshot_uses_bounded_retained_reader(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "notes.txt"
    content = b"retained source"
    snapshot = Win32FileSnapshot(
        metadata=_metadata(file_id=23, content=content, mtime_ns=700),
        content=content,
    )
    calls: list[tuple[tuple[str, ...], int | None]] = []

    class FakeAuthority:
        def read_file_snapshot(
            self,
            parts: tuple[str, ...],
            *,
            max_bytes: int | None = None,
        ) -> Win32FileSnapshot:
            calls.append((parts, max_bytes))
            return snapshot

    @contextmanager
    def fake_open(
        project_root: Path,
        *,
        root_identity: tuple[int, int] | None = None,
    ) -> Iterator[FakeAuthority]:
        assert project_root == tmp_path
        assert root_identity == (11, 22)
        yield FakeAuthority()

    monkeypatch.setattr(project_sdk, "_uses_win32_source_draft_authority", lambda: True)
    monkeypatch.setattr(project_sdk, "_source_draft_root_identity", lambda root: (tmp_path, (11, 22)))
    monkeypatch.setattr(project_sdk, "_open_win32_source_draft_authority", fake_open)

    payload, metadata = project_sdk._read_project_source_snapshot(tmp_path, path)

    assert payload == content
    assert metadata.st_size == len(content)
    assert metadata.st_mtime_ns == 700
    assert calls == [(("notes.txt",), project_sdk.MAX_PROJECT_SOURCE_TEXT_BYTES)]


@pytest.mark.unit
def test_win32_source_draft_mutation_guard_preserves_identity_and_content() -> None:
    path = Path("/project/source.txt")
    content = b"ParaDev draft"
    metadata = _metadata(file_id=31, content=content, mtime_ns=400)
    snapshot = Win32FileSnapshot(metadata=metadata, content=content)
    mutation = project_sdk._SourceDraftMutation(
        path=path,
        parent_identity=(11, 22),
        file_identity=(11, 31, len(content), 400),
        content_sha256=snapshot.content_sha256,
    )

    project_sdk._validate_win32_source_draft_mutation((11, 22), path, mutation, snapshot)

    changed = Win32FileSnapshot(metadata=metadata, content=b"external edit")
    with pytest.raises(ValueError, match="changed while it was verified"):
        project_sdk._validate_win32_source_draft_mutation((11, 22), path, mutation, changed)
    with pytest.raises(ValueError, match="parent directory changed"):
        project_sdk._validate_win32_source_draft_mutation((11, 99), path, mutation, snapshot)


@pytest.mark.unit
def test_win32_source_draft_batch_dispatches_guarded_writes_and_removal(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    notes = tmp_path / "notes.txt"
    created = tmp_path / "created.bin"
    obsolete = tmp_path / "obsolete.bin"
    state: dict[tuple[str, ...], Win32FileSnapshot] = {
        ("notes.txt",): Win32FileSnapshot(
            metadata=_metadata(file_id=41, content=b"old", mtime_ns=500),
            content=b"old",
        ),
        ("obsolete.bin",): Win32FileSnapshot(
            metadata=_metadata(file_id=42, content=b"obsolete", mtime_ns=600),
            content=b"obsolete",
        ),
    }
    calls: list[str] = []
    next_file_id = 100

    class FakeAuthority:
        path = tmp_path
        identity = (11, 22)

        def read_file_snapshot(
            self,
            parts: tuple[str, ...],
            *,
            max_bytes: int | None = None,
        ) -> Win32FileSnapshot | None:
            assert max_bytes is not None
            calls.append(f"backup:{'/'.join(parts)}")
            return state.get(parts)

        def entry_metadata(self, parts: tuple[str, ...]) -> Win32FileMetadata | None:
            snapshot = state.get(parts)
            return snapshot.metadata if snapshot is not None else None

        def guarded_write_bytes(
            self,
            parts: tuple[str, ...],
            payload: bytes,
            *,
            guard,
        ) -> tuple[tuple[int, int], Win32FileSnapshot]:
            nonlocal next_file_id
            calls.append(f"write:{'/'.join(parts)}")
            guard((11, 22), state.get(parts))
            next_file_id += 1
            snapshot = Win32FileSnapshot(
                metadata=_metadata(file_id=next_file_id, content=payload, mtime_ns=next_file_id),
                content=payload,
            )
            state[parts] = snapshot
            return (11, 22), snapshot

        def guarded_remove_file(
            self,
            parts: tuple[str, ...],
            *,
            guard,
            missing_ok: bool,
        ) -> tuple[tuple[int, int], Win32FileSnapshot | None]:
            calls.append(f"remove:{'/'.join(parts)}")
            snapshot = state.get(parts)
            guard((11, 22), snapshot)
            if snapshot is None and not missing_ok:
                raise FileNotFoundError(parts[-1])
            state.pop(parts, None)
            return (11, 22), snapshot

    authority = FakeAuthority()

    @contextmanager
    def fake_open(
        _project_root: Path,
        *,
        root_identity: tuple[int, int] | None = None,
    ) -> Iterator[FakeAuthority]:
        assert root_identity in {None, (11, 22)}
        yield authority

    monkeypatch.setattr(project_sdk, "_uses_win32_source_draft_authority", lambda: True)
    monkeypatch.setattr(project_sdk, "_open_win32_source_draft_authority", fake_open)

    project_sdk._apply_source_draft_mutations(
        tmp_path,
        edits=(
            {
                "path": notes,
                "text": "new",
                "expected_revision": (3, 500),
            },
        ),
        replacements=(
            {
                "path": created,
                "content": b"created",
                "expected_revision": project_sdk._SOURCE_DRAFT_EXPECTED_ABSENT,
            },
        ),
        removals=(
            {
                "path": obsolete,
                "expected_revision": (8, 600),
            },
        ),
        root_identity=(11, 22),
    )

    assert state[("notes.txt",)].content == b"new"
    assert state[("created.bin",)].content == b"created"
    assert ("obsolete.bin",) not in state
    assert calls == [
        "backup:notes.txt",
        "backup:created.bin",
        "backup:obsolete.bin",
        "write:notes.txt",
        "write:created.bin",
        "remove:obsolete.bin",
    ]


def _write_native_project(root: Path) -> Project:
    root.mkdir()
    (root / "paradev.yaml").write_text(
        "project_id: windows_source_draft\n"
        "title: Windows Source Draft\n"
        "game: hoi4\n"
        "source_roots: [src]\n"
        "output_root: build/mod\n"
        "build_root: .paradev/.cache/build\n",
        encoding="utf-8",
    )
    (root / "src").mkdir()
    return Project.load(root)


@pytest.mark.skipif(os.name != "nt", reason="Requires native Win32 retained-handle semantics.")
def test_native_win32_source_draft_applies_guarded_batch(tmp_path: Path) -> None:
    project = _write_native_project(tmp_path / "project")
    notes = project.root / "notes.txt"
    created = project.root / "created.bin"
    obsolete = project.root / "obsolete.bin"
    notes.write_text("old", encoding="utf-8")
    obsolete.write_bytes(b"obsolete")
    notes_revision = project.read_source_text(notes)
    obsolete_revision = obsolete.stat()

    payload = project.apply_source_draft(
        source_edits=[
            {
                "path": str(notes),
                "text": "new",
                "expected_size": notes_revision["size"],
                "expected_mtime_ns": notes_revision["mtime_ns"],
            }
        ],
        source_replacements=[
            {
                "path": str(created),
                "content_base64": "Y3JlYXRlZA==",
                "expected_absent": True,
            }
        ],
        source_removals=[
            {
                "path": str(obsolete),
                "expected_size": obsolete_revision.st_size,
                "expected_mtime_ns": str(obsolete_revision.st_mtime_ns),
            }
        ],
    )

    assert payload["written"] is True
    assert notes.read_text(encoding="utf-8") == "new"
    assert created.read_bytes() == b"created"
    assert not obsolete.exists()


@pytest.mark.skipif(os.name != "nt", reason="Requires native Win32 rollback semantics.")
def test_native_win32_source_draft_rolls_back_an_earlier_write(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _write_native_project(tmp_path / "project")
    first = project.root / "first.txt"
    second = project.root / "second.txt"
    first.write_text("first-original", encoding="utf-8")
    second.write_text("second-original", encoding="utf-8")
    original_write = project_sdk._write_source_draft_content

    def fail_second(
        project_root: Path,
        path: Path,
        content: bytes,
        **kwargs: object,
    ) -> project_sdk._SourceDraftMutation:
        if path == second:
            raise ValueError("simulated native late failure")
        return original_write(project_root, path, content, **kwargs)

    monkeypatch.setattr(project_sdk, "_write_source_draft_content", fail_second)

    with pytest.raises(ValueError, match="simulated native late failure"):
        project.apply_source_draft(
            source_edits=[
                {"path": str(first), "text": "first-draft"},
                {"path": str(second), "text": "second-draft"},
            ]
        )

    assert first.read_text(encoding="utf-8") == "first-original"
    assert second.read_text(encoding="utf-8") == "second-original"
