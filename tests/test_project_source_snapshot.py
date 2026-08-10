from __future__ import annotations

import threading
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest

import paradev.sdk.project as project_sdk
from paradev.sdk import Project, project_source_mutation_lock


def test_emitted_build_snapshot_serializes_batch_source_edits(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_root = tmp_path / "snapshot-project"
    module_root = project_root / "src/modules/focus/GER_sample"
    module_root.mkdir(parents=True)
    source_path = module_root / "def.txt"
    source_path.write_text("focus = { id = GER_sample x = 1 }\n", encoding="utf-8")
    (project_root / "paradev.yaml").write_text(
        "\n".join(
            (
                "project_id: snapshot_project",
                "title: Snapshot Project",
                "game: hoi4",
                "source_roots: [src]",
                "output_root: build/mod",
                "build_root: .paradev/.cache/build",
            )
        )
        + "\n",
        encoding="utf-8",
    )
    project = Project.load(project_root)

    mutex = threading.Lock()
    build_discovery_entered = threading.Event()
    release_build_discovery = threading.Event()
    edit_lock_attempted = threading.Event()
    edit_finished = threading.Event()
    errors: list[BaseException] = []
    build_results: list[object] = []
    original_discover_modules = Project._discover_modules

    @contextmanager
    def in_process_source_lock(locked_project: Project) -> Iterator[None]:
        assert locked_project is project
        thread_name = threading.current_thread().name
        if thread_name == "snapshot-edit":
            edit_lock_attempted.set()
        with mutex:
            yield

    @contextmanager
    def generated_lock(*_roots: Path) -> Iterator[None]:
        yield

    def gated_discover_modules(self: Project, **kwargs: object) -> object:
        if threading.current_thread().name == "snapshot-build":
            build_discovery_entered.set()
            assert release_build_discovery.wait(timeout=5)
        return original_discover_modules(self, **kwargs)

    def run_build() -> None:
        try:
            build_results.append(project.build(emit_artifacts=True))
        except BaseException as error:
            errors.append(error)

    def run_edit() -> None:
        try:
            project.write_module_files(
                [
                    {
                        "module_id": "focus/GER_sample",
                        "relative_path": "def.txt",
                        "text": "focus = { id = GER_sample x = 2 }\n",
                    }
                ]
            )
        except BaseException as error:
            errors.append(error)
        finally:
            edit_finished.set()

    monkeypatch.setattr(project_sdk, "_project_source_mutation_lock", in_process_source_lock)
    monkeypatch.setattr(project_sdk, "_project_build_mutation_lock", generated_lock)
    monkeypatch.setattr(Project, "_discover_modules", gated_discover_modules)

    build_thread = threading.Thread(target=run_build, name="snapshot-build")
    edit_thread = threading.Thread(target=run_edit, name="snapshot-edit")
    build_thread.start()
    assert build_discovery_entered.wait(timeout=5)
    edit_thread.start()
    assert edit_lock_attempted.wait(timeout=5)
    assert not edit_finished.wait(timeout=0.1)

    release_build_discovery.set()
    build_thread.join(timeout=10)
    edit_thread.join(timeout=10)

    assert not build_thread.is_alive()
    assert not edit_thread.is_alive()
    assert errors == []
    assert len(build_results) == 1
    result = build_results[0]
    assert getattr(result, "blocked") is False
    emitted = (project.output_root / "common/national_focus/GER_sample.txt").read_text(encoding="utf-8")
    assert "x = 1" in emitted
    assert "x = 2" not in emitted
    assert source_path.read_text(encoding="utf-8") == "focus = { id = GER_sample x = 2 }\n"


def test_public_project_source_mutation_lock_coordinates_sdk_edits(
    tmp_path: Path,
) -> None:
    project_root = tmp_path / "external-source-transaction"
    module_root = project_root / "src/modules/focus/GER_sample"
    module_root.mkdir(parents=True)
    source_path = module_root / "def.txt"
    source_path.write_text("focus = { id = GER_sample x = 1 }\n", encoding="utf-8")
    (project_root / "paradev.yaml").write_text(
        "\n".join(
            (
                "project_id: external_source_transaction",
                "title: External Source Transaction",
                "game: hoi4",
                "source_roots: [src]",
                "output_root: build/mod",
                "build_root: .paradev/.cache/build",
            )
        )
        + "\n",
        encoding="utf-8",
    )
    project = Project.load(project_root)
    edit_started = threading.Event()
    edit_finished = threading.Event()
    errors: list[BaseException] = []

    def run_edit() -> None:
        edit_started.set()
        try:
            project.write_module_file(
                "focus/GER_sample",
                "def.txt",
                text="focus = { id = GER_sample x = 2 }\n",
            )
        except BaseException as error:
            errors.append(error)
        finally:
            edit_finished.set()

    with project_source_mutation_lock(project_root):
        edit_thread = threading.Thread(target=run_edit, name="coordinated-sdk-edit")
        edit_thread.start()
        assert edit_started.wait(timeout=5)
        assert not edit_finished.wait(timeout=0.1)
        assert source_path.read_text(encoding="utf-8") == "focus = { id = GER_sample x = 1 }\n"

    edit_thread.join(timeout=10)
    assert not edit_thread.is_alive()
    assert errors == []
    assert edit_finished.is_set()
    assert source_path.read_text(encoding="utf-8") == "focus = { id = GER_sample x = 2 }\n"


def test_public_project_source_mutation_lock_is_reentrant_in_one_context(
    tmp_path: Path,
) -> None:
    finished = threading.Event()
    errors: list[BaseException] = []

    def enter_nested_lock() -> None:
        try:
            with project_source_mutation_lock(tmp_path):
                with project_source_mutation_lock(tmp_path):
                    finished.set()
        except BaseException as error:
            errors.append(error)
            finished.set()

    thread = threading.Thread(
        target=enter_nested_lock,
        name="nested-project-source-lock",
        daemon=True,
    )
    thread.start()

    assert finished.wait(timeout=5)
    thread.join(timeout=5)
    assert not thread.is_alive()
    assert not errors
