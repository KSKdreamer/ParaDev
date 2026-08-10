from __future__ import annotations

import os
import shutil
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import pytest

import paradev.hb as hb_surface
import paradev.sdk.project as project_sdk
from paradev.sdk import Project


def _write_project(root: Path, source_roots: tuple[str, ...] = ("src",)) -> Project:
    root.mkdir(parents=True)
    roots = ", ".join(source_roots)
    (root / "paradev.yaml").write_text(
        "\n".join(
            (
                "project_id: metadata_cleanup",
                "title: Metadata Cleanup",
                "game: hoi4",
                f"source_roots: [{roots}]",
                "output_root: output",
                "build_root: build",
                "",
            )
        ),
        encoding="utf-8",
    )
    return Project.load(root)


def _write_module(
    project_root: Path,
    object_id: str,
    metadata: bytes | None,
    *,
    source_root: str = "src",
    with_definition: bool = True,
) -> Path:
    module_root = project_root / source_root / "modules" / "idea" / object_id
    module_root.mkdir(parents=True)
    if with_definition:
        (module_root / "def.txt").write_text(
            f"{object_id} = {{}}\n",
            encoding="utf-8",
        )
    if metadata is not None:
        (module_root / "meta.yaml").write_bytes(metadata)
    return module_root


def test_module_metadata_cleanup_plans_and_applies_exact_byte_edit(
    tmp_path: Path,
) -> None:
    root = tmp_path / "project"
    project = _write_project(root)
    module_root = _write_module(
        root,
        "FRIENDSHIP",
        ("# Keep this note.\r\n" "type: idea\r\n" 'title: "友谊与工业"\r\n' "settings:\r\n" "  value: 2\r\n").encode(),
    )
    metadata_path = module_root / "meta.yaml"
    expected = metadata_path.read_bytes().replace(b"type: idea\r\n", b"", 1)

    plan = project.clean_module_metadata(module_id="idea/FRIENDSHIP")
    repeated = project.clean_module_metadata(module_id="idea/FRIENDSHIP")

    assert plan["schema"] == "paradev.sdk.module_metadata_cleanup.v1"
    assert plan["policy"] == "paradev.module-metadata-cleanup-policy.v1"
    assert plan["status"] == "planned"
    assert plan["blocked"] is False
    assert plan["applied"] is False
    assert plan["written"] is False
    assert plan["plan_hash"] == repeated["plan_hash"]
    assert plan["counts"] == {
        "modules_scanned": 1,
        "metadata_files_scanned": 1,
        "update": 1,
        "remove": 0,
        "unchanged": 0,
        "blocked": 0,
        "changed": 1,
    }
    assert plan["files"][0]["action"] == "update"
    assert plan["files"][0]["removed_keys"] == ["type"]

    result = project.clean_module_metadata(
        module_id="idea/FRIENDSHIP",
        write=True,
        plan_hash=str(plan["plan_hash"]),
    )

    assert result["status"] == "cleaned"
    assert result["applied"] is True
    assert result["written"] is True
    assert result["catalog_mutation"]["status"] == "not_configured"
    assert metadata_path.read_bytes() == expected
    assert (
        Project.load(root)
        .discover_modules(
            profile="hoi4",
            module_id="idea/FRIENDSHIP",
        )
        .modules
    )


def test_module_metadata_cleanup_rejects_missing_and_stale_plans_without_catalog_invalidation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "project"
    project = _write_project(root)
    module_root = _write_module(
        root,
        "A",
        b"type: idea\ntitle: Before\n",
    )
    metadata_path = module_root / "meta.yaml"
    plan = project.clean_module_metadata(module_id="idea/A")
    entered = 0

    @contextmanager
    def unexpected_scope(
        _project: Project,
        *,
        enabled: bool = True,
    ) -> Iterator[bool]:
        nonlocal entered
        entered += 1
        yield enabled

    monkeypatch.setattr(
        hb_surface,
        "_module_catalog_mutation_scope",
        unexpected_scope,
    )

    missing = project.clean_module_metadata(
        module_id="idea/A",
        write=True,
    )
    metadata_path.write_bytes(b"type: idea\ntitle: After\n")
    stale = project.clean_module_metadata(
        module_id="idea/A",
        write=True,
        plan_hash=str(plan["plan_hash"]),
    )

    assert missing["status"] == "blocked"
    assert missing["diagnostics"][-1]["code"] == ("module_metadata_cleanup.plan_hash_required")
    assert stale["status"] == "blocked"
    assert stale["diagnostics"][-1]["code"] == ("module_metadata_cleanup.plan_hash_mismatch")
    assert entered == 0
    assert metadata_path.read_bytes() == b"type: idea\ntitle: After\n"
    assert not (root / ".paradev").exists()


def test_module_metadata_cleanup_removes_type_only_file_but_keeps_module(
    tmp_path: Path,
) -> None:
    root = tmp_path / "project"
    project = _write_project(root)
    module_root = _write_module(
        root,
        "A",
        b"type: idea\n\n  ",
    )
    plan = project.clean_module_metadata(module_id="idea/A")

    assert plan["files"][0]["action"] == "remove"
    result = project.clean_module_metadata(
        module_id="idea/A",
        write=True,
        plan_hash=str(plan["plan_hash"]),
    )

    assert result["status"] == "cleaned"
    assert not (module_root / "meta.yaml").exists()
    modules = (
        Project.load(root)
        .discover_modules(
            profile="hoi4",
            module_id="idea/A",
        )
        .modules
    )
    assert [module.module_id for module in modules] == ["idea/A"]


def test_module_metadata_cleanup_preserves_identity_for_meta_only_module(
    tmp_path: Path,
) -> None:
    root = tmp_path / "project"
    project = _write_project(root)
    module_root = _write_module(
        root,
        "A",
        b"type: idea\n",
        with_definition=False,
    )
    plan = project.clean_module_metadata(module_id="idea/A")

    assert plan["files"][0]["action"] == "update"
    assert plan["files"][0]["planned"]["size_bytes"] == 3
    assert plan["diagnostics"][0]["code"] == ("module_metadata_cleanup.identity_marker_preserved")
    result = project.clean_module_metadata(
        module_id="idea/A",
        write=True,
        plan_hash=str(plan["plan_hash"]),
    )

    assert result["status"] == "cleaned"
    assert (module_root / "meta.yaml").read_bytes() == b"{}\n"
    modules = (
        Project.load(root)
        .discover_modules(
            profile="hoi4",
            module_id="idea/A",
        )
        .modules
    )
    assert [module.module_id for module in modules] == ["idea/A"]


def test_module_metadata_cleanup_keeps_comment_only_remainder_valid_yaml(
    tmp_path: Path,
) -> None:
    root = tmp_path / "project"
    project = _write_project(root)
    module_root = _write_module(
        root,
        "A",
        b"# Keep this note.\ntype: idea\n",
    )
    plan = project.clean_module_metadata(module_id="idea/A")
    result = project.clean_module_metadata(
        module_id="idea/A",
        write=True,
        plan_hash=str(plan["plan_hash"]),
    )

    assert result["status"] == "cleaned"
    assert (module_root / "meta.yaml").read_bytes() == (b"# Keep this note.\n{}\n")
    discovery = Project.load(root).discover_modules(
        profile="hoi4",
        module_id="idea/A",
    )
    assert discovery.modules
    assert not [diagnostic for diagnostic in discovery.diagnostics if diagnostic.code == "metadata.invalid_yaml"]


def test_module_metadata_cleanup_exact_selector_requires_source_root_for_duplicates(
    tmp_path: Path,
) -> None:
    root = tmp_path / "project"
    project = _write_project(root, ("src", "imports"))
    _write_module(root, "A", b"type: idea\ntitle: Primary\n")
    _write_module(
        root,
        "A",
        b"type: idea\ntitle: Imported\n",
        source_root="imports",
    )

    with pytest.raises(ValueError, match="multiple source roots"):
        project.clean_module_metadata(module_id="idea/A")

    plan = project.clean_module_metadata(
        module_id="idea/A",
        source_root="imports",
    )

    assert plan["counts"]["modules_scanned"] == 1
    assert plan["selectors"]["source_root"] == str(root / "imports")
    assert plan["files"][0]["source_root"] == str(root / "imports")


def test_module_metadata_cleanup_exact_selector_rejects_empty_folder(
    tmp_path: Path,
) -> None:
    root = tmp_path / "project"
    project = _write_project(root)
    empty_root = root / "src" / "modules" / "idea" / "EMPTY"
    empty_root.mkdir(parents=True)

    assert not project.discover_modules(profile="hoi4").modules
    with pytest.raises(ValueError, match="Unknown module: idea/EMPTY"):
        project.clean_module_metadata(module_id="idea/EMPTY")


def test_module_metadata_cleanup_deduplicates_equivalent_source_roots(
    tmp_path: Path,
) -> None:
    root = tmp_path / "project"
    project = _write_project(root, ("src", "./src"))
    module_root = _write_module(
        root,
        "A",
        b"type: idea\ntitle: One source\n",
    )

    plan = project.clean_module_metadata(module_id="idea/A")

    assert len(project.source_roots) == 2
    assert plan["counts"]["modules_scanned"] == 1
    assert plan["counts"]["metadata_files_scanned"] == 1
    result = project.clean_module_metadata(
        module_id="idea/A",
        write=True,
        plan_hash=str(plan["plan_hash"]),
    )

    assert result["status"] == "cleaned"
    assert result["written"] is True
    assert (module_root / "meta.yaml").read_bytes() == b"title: One source\n"


def test_module_metadata_cleanup_blocks_mismatched_visible_type(
    tmp_path: Path,
) -> None:
    root = tmp_path / "project"
    project = _write_project(root)
    _write_module(root, "A", b"type: event\ntitle: Wrong\n")

    plan = project.clean_module_metadata(module_id="idea/A")

    assert plan["status"] == "blocked"
    assert plan["counts"]["blocked"] == 1
    assert plan["files"][0]["action"] == "blocked"
    assert plan["diagnostics"][0]["code"] == ("module_metadata_cleanup.type_mismatch")


def test_module_metadata_cleanup_exact_noop_apply_does_not_open_catalog_scope(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "project"
    project = _write_project(root)
    _write_module(root, "A", b"title: Already minimal\n")
    plan = project.clean_module_metadata(module_id="idea/A")

    @contextmanager
    def unexpected_scope(
        _project: Project,
        *,
        enabled: bool = True,
    ) -> Iterator[bool]:
        raise AssertionError("No-op cleanup must not enter Catalog mutation scope.")
        yield enabled

    monkeypatch.setattr(
        hb_surface,
        "_module_catalog_mutation_scope",
        unexpected_scope,
    )

    result = project.clean_module_metadata(
        module_id="idea/A",
        write=True,
        plan_hash=str(plan["plan_hash"]),
    )

    assert result["status"] == "unchanged"
    assert result["applied"] is True
    assert result["written"] is False
    assert "catalog_mutation" not in result
    assert not (root / ".paradev").exists()


def test_module_metadata_cleanup_rolls_back_prior_file_on_later_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "project"
    project = _write_project(root)
    first_root = _write_module(
        root,
        "A",
        b"type: idea\ntitle: First\n",
    )
    second_root = _write_module(
        root,
        "B",
        b"type: idea\ntitle: Second\n",
    )
    first_path = first_root / "meta.yaml"
    second_path = second_root / "meta.yaml"
    first_before = first_path.read_bytes()
    second_before = second_path.read_bytes()
    plan = project.clean_module_metadata(family="idea")
    original_write = project_sdk._write_source_draft_content

    def fail_second_write(
        project_root: Path,
        path: Path,
        content: bytes | Path,
        **kwargs: object,
    ) -> object:
        if path == second_path and kwargs.get("expected_mutation") is None:
            raise OSError("simulated second-file failure")
        return original_write(
            project_root,
            path,
            content,
            **kwargs,
        )

    monkeypatch.setattr(
        project_sdk,
        "_write_source_draft_content",
        fail_second_write,
    )

    result = project.clean_module_metadata(
        family="idea",
        write=True,
        plan_hash=str(plan["plan_hash"]),
    )

    assert result["status"] == "blocked"
    assert result["written"] is False
    assert result["diagnostics"][-1]["code"] == ("module_metadata_cleanup.concurrent_change")
    assert first_path.read_bytes() == first_before
    assert second_path.read_bytes() == second_before


def test_module_metadata_cleanup_rejects_same_revision_content_race(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "project"
    project = _write_project(root)
    module_root = _write_module(
        root,
        "A",
        b"type: idea\ntitle: One\n",
    )
    metadata_path = module_root / "meta.yaml"
    plan = project.clean_module_metadata(module_id="idea/A")
    original_apply = project_sdk._apply_module_metadata_cleanup

    def race_then_apply(
        mutation_root: Path,
        entries: object,
        *,
        root_identity: tuple[int, int],
    ) -> None:
        revision = metadata_path.stat()
        metadata_path.write_bytes(b"type: idea\ntitle: Two\n")
        os.utime(
            metadata_path,
            ns=(revision.st_atime_ns, revision.st_mtime_ns),
        )
        original_apply(
            mutation_root,
            entries,
            root_identity=root_identity,
        )

    monkeypatch.setattr(
        project_sdk,
        "_apply_module_metadata_cleanup",
        race_then_apply,
    )

    result = project.clean_module_metadata(
        module_id="idea/A",
        write=True,
        plan_hash=str(plan["plan_hash"]),
    )

    assert result["status"] == "blocked"
    assert result["written"] is False
    assert result["diagnostics"][-1]["code"] == ("module_metadata_cleanup.concurrent_change")
    assert metadata_path.read_bytes() == b"type: idea\ntitle: Two\n"


def test_module_metadata_cleanup_reports_displaced_target_recovery(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "project"
    project = _write_project(root)
    module_root = _write_module(
        root,
        "A",
        b"type: idea\ntitle: One\n",
    )
    metadata_path = module_root / "meta.yaml"
    original = metadata_path.read_bytes()
    plan = project.clean_module_metadata(module_id="idea/A")
    link = project_sdk.os.link
    injected = False

    def inject_external_directory(
        source_name: str,
        target_name: str,
        **kwargs: object,
    ) -> None:
        nonlocal injected
        link(source_name, target_name, **kwargs)
        if not injected and source_name == metadata_path.name and target_name.endswith(".displaced"):
            injected = True
            metadata_path.unlink()
            metadata_path.mkdir()
            (metadata_path / "external.txt").write_text(
                "external",
                encoding="utf-8",
            )

    monkeypatch.setattr(
        project_sdk.os,
        "link",
        inject_external_directory,
    )

    result = project.clean_module_metadata(
        module_id="idea/A",
        write=True,
        plan_hash=str(plan["plan_hash"]),
    )

    recovery_path = Path(str(result["recovery"]["path"]))
    displaced = result["recovery"]["displaced_target"]
    displaced_path = Path(str(displaced["recovery_path"]))
    assert injected is True
    assert result["status"] == "blocked"
    assert result["partially_written"] is True
    assert result["partial_state"] == "unknown"
    assert result["diagnostics"][-1]["code"] == ("module_metadata_cleanup.rollback_incomplete")
    assert displaced["destination_exists"] is True
    assert metadata_path.is_dir()
    assert (metadata_path / "external.txt").read_text(encoding="utf-8") == "external"
    assert displaced_path.read_bytes() == original
    assert (recovery_path / "recovery.json").is_file()


def test_module_metadata_cleanup_reports_incomplete_rollback_and_recovery(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "project"
    project = _write_project(root)
    first_root = _write_module(
        root,
        "A",
        b"type: idea\ntitle: First\n",
    )
    second_root = _write_module(
        root,
        "B",
        b"type: idea\ntitle: Second\n",
    )
    first_path = first_root / "meta.yaml"
    second_path = second_root / "meta.yaml"
    first_before = first_path.read_bytes()
    second_before = second_path.read_bytes()
    plan = project.clean_module_metadata(family="idea")
    original_write = project_sdk._write_source_draft_content

    def fail_apply_and_rollback(
        project_root: Path,
        path: Path,
        content: bytes | Path,
        **kwargs: object,
    ) -> object:
        if path == second_path and kwargs.get("expected_mutation") is None:
            raise OSError("simulated second-file failure")
        if path == first_path and kwargs.get("expected_mutation") is not None:
            raise OSError("simulated rollback failure")
        return original_write(
            project_root,
            path,
            content,
            **kwargs,
        )

    monkeypatch.setattr(
        project_sdk,
        "_write_source_draft_content",
        fail_apply_and_rollback,
    )

    result = project.clean_module_metadata(
        family="idea",
        write=True,
        plan_hash=str(plan["plan_hash"]),
    )

    recovery_path = Path(str(result["recovery"]["path"]))
    try:
        assert result["status"] == "blocked"
        assert result["written"] is False
        assert result["partially_written"] is True
        assert result["partial_state"] == "unknown"
        assert result["diagnostics"][-1]["code"] == ("module_metadata_cleanup.rollback_incomplete")
        assert recovery_path.is_dir()
        assert first_path.read_bytes() != first_before
        assert second_path.read_bytes() == second_before
    finally:
        shutil.rmtree(recovery_path, ignore_errors=True)


def test_module_metadata_cleanup_requires_scoped_apply_across_external_roots(
    tmp_path: Path,
) -> None:
    root = tmp_path / "project"
    external = tmp_path / "external"
    project = _write_project(root, ("src", str(external)))
    _write_module(root, "A", b"type: idea\ntitle: Local\n")
    external_module = external / "modules" / "idea" / "B"
    external_module.mkdir(parents=True)
    (external_module / "def.txt").write_text("B = {}\n", encoding="utf-8")
    (external_module / "meta.yaml").write_bytes(b"type: idea\ntitle: External\n")

    plan = project.clean_module_metadata(family="idea")

    assert plan["status"] == "blocked"
    assert plan["counts"]["changed"] == 2
    assert plan["diagnostics"][-1]["code"] == ("module_metadata_cleanup.multi_root_transaction")
