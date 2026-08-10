from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

import pytest

import paradev.build._fs as build_fs
import paradev.build.artifacts as build_artifacts
import paradev.build.publication as build_publication
from paradev.build import Artifact, BuildContext, BuildRegistry, Collection, Module, PDXTextWriter
from paradev.sdk import Project, ProjectManifestError


class _SingleArtifactFamily:
    family = "focus"

    def emit(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> tuple[Artifact, ...]:
        del ctx, collections
        return tuple(
            Artifact(
                path=f"generated/{module.module_id.split('/', 1)[1]}.txt",
                artifact_type="pdx",
                owner=f"module:{module.module_id}",
                metadata={"family": module.family, "module_id": module.module_id},
                payload=f"id = {module.module_id}\n",
            )
            for module in modules
        )


class _MutableArtifactFamily:
    family = "focus"

    def __init__(self, paths: tuple[str, ...]) -> None:
        self.paths = paths
        self.replaces: tuple[str, ...] = ()

    def emit(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> tuple[Artifact, ...]:
        del ctx, collections
        module = modules[0]
        artifacts: list[Artifact] = []
        for path in self.paths:
            metadata: dict[str, object] = {
                "family": module.family,
                "module_id": module.module_id,
            }
            if self.replaces:
                metadata.update(
                    {
                        "publication_scope": "project",
                        "publication_replaces": list(self.replaces),
                    }
                )
            artifacts.append(
                Artifact(
                    path=path,
                    artifact_type="pdx",
                    owner=f"module:{module.module_id}",
                    metadata=metadata,
                    payload=f"path = {path}\n",
                )
            )
        return tuple(artifacts)


def test_cached_build_refuses_to_replace_an_untracked_existing_artifact(tmp_path: Path) -> None:
    project = _write_project(tmp_path / "project", project_id="untracked_leaf", module_id="X")
    user_file = project.output_root / "common/national_focus/X.txt"
    user_file.parent.mkdir(parents=True)
    user_file.write_text("USER DATA\n", encoding="utf-8")

    with pytest.raises(ValueError):
        project.build(emit_artifacts=True)

    assert user_file.read_text(encoding="utf-8") == "USER DATA\n"


def test_configured_output_root_symlink_is_rejected_before_publication(tmp_path: Path) -> None:
    root = tmp_path / "project"
    user_root = tmp_path / "user-output"
    user_root.mkdir()
    victim = user_root / "victim.txt"
    victim.write_text("safe\n", encoding="utf-8")
    output_link = root / "output-link"
    output_link.parent.mkdir(parents=True)
    try:
        output_link.symlink_to(user_root, target_is_directory=True)
    except OSError as error:
        pytest.skip(f"Directory symlinks are unavailable: {error}")
    project = _write_project(
        root,
        project_id="symlinked_output",
        module_id="X",
        output_root="output-link",
    )

    with pytest.raises(ValueError):
        project.build(emit_artifacts=True)

    assert victim.read_text(encoding="utf-8") == "safe\n"
    assert not (user_root / "common/national_focus/X.txt").exists()
    assert not (user_root / "descriptor.mod").exists()


def test_default_output_root_rejects_a_project_id_path_escape(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "project"
    (root / "src").mkdir(parents=True)
    mod_root = tmp_path / "mod-root"
    mod_root.mkdir()
    sentinel = tmp_path / "sentinel.txt"
    sentinel.write_text("safe\n", encoding="utf-8")
    monkeypatch.setenv("PARADEV_HOI4_MOD_ROOT", str(mod_root))
    (root / "paradev.yaml").write_text(
        "\n".join(
            (
                "project_id: ../../escaped",
                "title: Escaped",
                "game: hoi4",
                "source_roots: [src]",
                "build_root: .paradev/.cache/build",
                "",
            )
        ),
        encoding="utf-8",
    )

    with pytest.raises(ProjectManifestError, match="safe filename segment"):
        Project.load(root)

    assert sentinel.read_text(encoding="utf-8") == "safe\n"
    assert not (tmp_path / "escaped").exists()


def test_writer_failure_preserves_ordinary_stale_file_and_recovery_row(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _write_project(tmp_path / "project", project_id="stale_retry", module_id="X")
    project.build(emit_artifacts=True)
    generated = project.output_root / "common/national_focus/X.txt"
    generated_payload = generated.read_bytes()
    module_root = project.source_roots[0] / "modules/focus/X"
    shutil.rmtree(module_root)
    original_write_artifacts = build_artifacts._write_artifacts_anchored

    def fail_before_writing(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise RuntimeError("simulated writer failure")

    monkeypatch.setattr(build_artifacts, "_write_artifacts_anchored", fail_before_writing)
    with pytest.raises(RuntimeError, match="simulated writer failure"):
        project.build(emit_artifacts=True)

    ledger_path = project.build_root / build_publication.EMITTED_ARTIFACTS_NAME
    pending = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert pending["state"] == "pending"
    assert "common/national_focus/X.txt" in {row["path"] for row in pending["artifacts"]}
    assert generated.read_bytes() == generated_payload
    failed_state = build_publication.load_publication_state(
        project.build_root,
        project_id=project.project_id,
        project_root=project.root,
        output_root=project.output_root,
    )
    assert failed_state.complete is False
    assert failed_state.whole_project_baseline is True

    monkeypatch.setattr(build_artifacts, "_write_artifacts_anchored", original_write_artifacts)
    result = project.build(emit_artifacts=True)

    assert result.blocked is False
    assert not generated.exists()
    complete = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert complete["state"] == "complete"
    assert "common/national_focus/X.txt" not in {row["path"] for row in complete["artifacts"]}
    recovered_state = build_publication.load_publication_state(
        project.build_root,
        project_id=project.project_id,
        project_root=project.root,
        output_root=project.output_root,
    )
    assert recovered_state.complete is True
    assert recovered_state.whole_project_baseline is True


def test_retry_adopts_exact_outputs_left_before_a_ledger_checkpoint(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _write_project(tmp_path / "project", project_id="checkpoint_retry", module_id="X")
    original_record = build_publication.record_written_artifacts

    def fail_checkpoint(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise OSError("simulated ledger ENOSPC")

    monkeypatch.setattr(build_publication, "record_written_artifacts", fail_checkpoint)
    with pytest.raises(OSError, match="ledger ENOSPC"):
        project.build(emit_artifacts=True)

    generated = project.output_root / "common/national_focus/X.txt"
    expected = generated.read_bytes()
    monkeypatch.setattr(build_publication, "record_written_artifacts", original_record)

    result = project.build(emit_artifacts=True)

    assert result.blocked is False
    assert generated.read_bytes() == expected


def test_cached_publication_reuses_projected_rows_and_in_memory_checkpoints(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _write_project(tmp_path / "project", project_id="checkpoint_reuse", module_id="X")
    project.build(emit_artifacts=True)
    original_projection = build_publication.emitted_artifact_rows
    projection_calls = 0

    def track_projection(result):
        nonlocal projection_calls
        projection_calls += 1
        return original_projection(result)

    def unexpected_reload(*args: object, **kwargs: object):
        del args, kwargs
        raise AssertionError("publication checkpoints must stay in the active transaction")

    monkeypatch.setattr(build_publication, "emitted_artifact_rows", track_projection)
    monkeypatch.setattr(build_publication, "load_emitted_artifact_rows", unexpected_reload)

    result = project.build(emit_artifacts=True)

    assert result.blocked is False
    assert projection_calls == 1
    state = build_publication.load_publication_state(
        project.build_root,
        project_id=project.project_id,
        project_root=project.root,
        output_root=project.output_root,
    )
    assert state.complete is True


def test_manifest_only_build_claims_its_build_root_for_a_later_full_build(
    tmp_path: Path,
) -> None:
    project = _write_project(tmp_path / "project", project_id="manifest_only", module_id="X")

    project.build(emit_manifests=True)
    marker = project.build_root / ".paradev-publication.json"
    assert marker.is_file()

    result = project.build(emit_artifacts=True, emit_manifests=True, full_rebuild=True)

    assert result.blocked is False
    assert (project.output_root / "common/national_focus/X.txt").is_file()
    assert marker.is_file()


def test_manifest_only_build_preserves_markerless_v2_build_ownership(
    tmp_path: Path,
) -> None:
    project = _write_project(tmp_path / "project", project_id="v2_migration", module_id="X")
    project.build(emit_artifacts=True, emit_manifests=True)
    marker = project.build_root / ".paradev-publication.json"
    marker.unlink()

    project.build(emit_manifests=True)

    marker_payload = json.loads(marker.read_text(encoding="utf-8"))
    assert marker_payload["full_clean_owned"] is True
    result = project.build(emit_artifacts=True, emit_manifests=True, full_rebuild=True)
    assert result.blocked is False


def test_cached_build_repairs_publication_device_identity_after_remount(
    tmp_path: Path,
) -> None:
    project = _write_project(
        tmp_path / "project",
        project_id="device_remount",
        module_id="X",
    )
    project.build(emit_artifacts=True, emit_manifests=True)
    marker_paths = (
        project.build_root / ".paradev-publication.json",
        project.output_root / ".paradev-publication.json",
    )
    ledger_path = project.build_root / ".emitted-artifacts.json"
    for marker_path in marker_paths:
        payload = json.loads(marker_path.read_text(encoding="utf-8"))
        payload["identity"]["root"]["device"] += 1
        marker_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    for root in ledger["identity"]["roots"].values():
        root["device"] += 1
    ledger_path.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    result = project.build(emit_artifacts=True, emit_manifests=True)

    assert result.blocked is False
    for marker_path in marker_paths:
        payload = json.loads(marker_path.read_text(encoding="utf-8"))
        assert payload["identity"]["root"]["device"] == marker_path.parent.stat().st_dev
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert ledger["identity"]["roots"]["build"]["device"] == project.build_root.stat().st_dev
    assert ledger["identity"]["roots"]["output"]["device"] == project.output_root.stat().st_dev


def test_foreign_launcher_descriptor_is_refused_before_artifact_publication(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mod_root = tmp_path / "hoi4-mod"
    mod_root.mkdir()
    monkeypatch.setenv("PARADEV_HOI4_MOD_ROOT", str(mod_root))
    launcher = mod_root / "foreign_launcher.mod"
    launcher.write_text("USER DATA\n", encoding="utf-8")
    project = _write_project(
        tmp_path / "project",
        project_id="foreign_launcher",
        module_id="X",
        output_root=str(mod_root / "foreign_launcher"),
    )

    with pytest.raises(ValueError, match="launcher descriptor is not owned"):
        project.build(emit_artifacts=True)

    assert launcher.read_text(encoding="utf-8") == "USER DATA\n"
    assert not (project.output_root / "common/national_focus/X.txt").exists()


def test_distinct_projects_cannot_claim_the_same_output_root(tmp_path: Path) -> None:
    shared_output = tmp_path / "shared-output"
    alpha = _write_project(
        tmp_path / "alpha",
        project_id="alpha",
        module_id="ALPHA",
        output_root=str(shared_output),
    )
    beta = _write_project(
        tmp_path / "beta",
        project_id="beta",
        module_id="BETA",
        output_root=str(shared_output),
    )
    registry = BuildRegistry().add(_SingleArtifactFamily()).add_writer(PDXTextWriter())

    alpha.build(registry=registry, emit_artifacts=True)
    alpha_file = shared_output / "generated/ALPHA.txt"
    assert alpha_file.is_file()

    with pytest.raises(ValueError):
        beta.build(registry=registry, emit_artifacts=True)

    assert alpha_file.read_text(encoding="utf-8") == "id = focus/ALPHA\n"
    assert not (shared_output / "generated/BETA.txt").exists()


def test_second_stale_deletion_failure_keeps_every_predecessor_recoverable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _write_project(tmp_path / "project", project_id="stale_journal", module_id="ALPHA")
    beta_root = project.source_roots[0] / "modules/focus/BETA"
    beta_root.mkdir(parents=True)
    (beta_root / "def.txt").write_text("focus = { id = BETA }\n", encoding="utf-8")
    project.build(emit_artifacts=True)
    ledger_path = project.build_root / build_publication.EMITTED_ARTIFACTS_NAME
    original_rows = json.loads(ledger_path.read_text(encoding="utf-8"))["artifacts"]
    tracked_paths = [str(row["path"]) for row in original_rows if str(row["path"]).startswith("common/national_focus/")]
    assert len(tracked_paths) == 2
    shutil.rmtree(project.source_roots[0] / "modules/focus")
    original_delete = build_publication._delete_tracked_artifact
    calls = 0

    def fail_second_delete(*args: object, **kwargs: object) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("simulated second stale deletion failure")
        original_delete(*args, **kwargs)

    monkeypatch.setattr(build_publication, "_delete_tracked_artifact", fail_second_delete)
    with pytest.raises(OSError, match="second stale deletion"):
        project.build(emit_artifacts=True)

    pending = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert pending["state"] == "pending"
    pending_tracked_paths = set(tracked_paths).intersection({row["path"] for row in pending["artifacts"]})
    assert len(pending_tracked_paths) == 1
    assert (project.output_root / pending_tracked_paths.pop()).is_file()
    assert sum((project.output_root / path).is_file() for path in tracked_paths) == 1

    monkeypatch.setattr(build_publication, "_delete_tracked_artifact", original_delete)
    result = project.build(emit_artifacts=True)

    assert result.blocked is False
    assert all(not (project.output_root / path).exists() for path in tracked_paths)
    complete = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert complete["state"] == "complete"
    assert all(row["path"] not in tracked_paths for row in complete["artifacts"])


def test_writer_failure_during_path_migration_preserves_predecessor_and_pending_ledger(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _write_project(tmp_path / "project", project_id="migration_recovery", module_id="X")
    family = _MutableArtifactFamily(("generated/old.txt", "generated/stale.txt"))
    registry = BuildRegistry().add(family).add_writer(PDXTextWriter())
    project.build(registry=registry, emit_artifacts=True)
    old_path = project.output_root / "generated/old.txt"
    new_path = project.output_root / "generated/new.txt"
    stale_path = project.output_root / "generated/stale.txt"
    old_payload = old_path.read_bytes()
    stale_payload = stale_path.read_bytes()
    family.paths = ("generated/new.txt",)
    family.replaces = ("generated/old.txt",)
    original_write = build_artifacts._write_artifacts_anchored

    def fail_before_writing(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise RuntimeError("simulated migration writer failure")

    monkeypatch.setattr(build_artifacts, "_write_artifacts_anchored", fail_before_writing)
    with pytest.raises(RuntimeError, match="migration writer failure"):
        project.build(registry=registry, emit_artifacts=True)

    ledger_path = project.build_root / build_publication.EMITTED_ARTIFACTS_NAME
    pending = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert pending["state"] == "pending"
    pending_paths = {row["path"] for row in pending["artifacts"]}
    assert {"generated/old.txt", "generated/stale.txt"}.issubset(pending_paths)
    assert old_path.read_bytes() == old_payload
    assert stale_path.read_bytes() == stale_payload
    assert not new_path.exists()

    monkeypatch.setattr(build_artifacts, "_write_artifacts_anchored", original_write)
    result = project.build(registry=registry, emit_artifacts=True)

    assert result.blocked is False
    assert not old_path.exists()
    assert not stale_path.exists()
    assert new_path.read_text(encoding="utf-8") == "path = generated/new.txt\n"
    complete = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert complete["state"] == "complete"
    complete_paths = {row["path"] for row in complete["artifacts"]}
    assert "generated/old.txt" not in complete_paths
    assert "generated/new.txt" in complete_paths


def test_structural_blocker_checkpoint_recovers_after_writer_checkpoint_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _write_project(tmp_path / "project", project_id="structural_recovery", module_id="X")
    family = _MutableArtifactFamily(("generated/shape",))
    registry = BuildRegistry().add(family).add_writer(PDXTextWriter())
    project.build(registry=registry, emit_artifacts=True)
    family.paths = ("generated/shape/child.txt",)
    original_write = build_artifacts._write_artifacts_anchored

    def write_then_fail(*args: object, **kwargs: object) -> None:
        original_write(*args, **kwargs)
        raise RuntimeError("simulated post-write failure")

    monkeypatch.setattr(build_artifacts, "_write_artifacts_anchored", write_then_fail)
    with pytest.raises(RuntimeError, match="post-write failure"):
        project.build(registry=registry, emit_artifacts=True)

    child = project.output_root / "generated/shape/child.txt"
    assert child.is_file()
    ledger_path = project.build_root / build_publication.EMITTED_ARTIFACTS_NAME
    pending = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert pending["state"] == "pending"
    pending_rows = {row["path"]: row for row in pending["artifacts"]}
    assert pending_rows["generated/shape"]["pending_removal"] is True
    assert "generated/shape/child.txt" in pending_rows

    monkeypatch.setattr(build_artifacts, "_write_artifacts_anchored", original_write)
    result = project.build(registry=registry, emit_artifacts=True)

    assert result.blocked is False
    assert child.read_text(encoding="utf-8") == "path = generated/shape/child.txt\n"
    complete = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert complete["state"] == "complete"
    assert [row["path"] for row in complete["artifacts"]] == ["generated/shape/child.txt"]


@pytest.mark.skipif(os.name == "nt", reason="This fixture injects POSIX st_dev metadata; Win32 coverage uses retained volume identities.")
def test_full_clean_refuses_to_cross_a_nested_device_boundary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "output"
    nested = root / "mounted"
    nested.mkdir(parents=True)
    victim = nested / "victim.txt"
    victim.write_text("safe\n", encoding="utf-8")
    original_stat = build_fs.os.stat

    with build_fs.open_anchored_directory(root, create=False) as authority:

        def cross_device_stat(
            path: object,
            *args: object,
            dir_fd: int | None = None,
            follow_symlinks: bool = True,
            **kwargs: object,
        ) -> os.stat_result:
            metadata = original_stat(
                path,
                *args,
                dir_fd=dir_fd,
                follow_symlinks=follow_symlinks,
                **kwargs,
            )
            if path != "mounted" or dir_fd is None:
                return metadata
            values = list(metadata)
            values[2] = metadata.st_dev + 1
            return os.stat_result(values)

        monkeypatch.setattr(build_fs.os, "stat", cross_device_stat)
        with pytest.raises(ValueError, match="filesystem boundary"):
            authority.clear()

    assert victim.read_text(encoding="utf-8") == "safe\n"


def _write_project(
    root: Path,
    *,
    project_id: str,
    module_id: str,
    output_root: str = "build/mod",
) -> Project:
    module_root = root / f"src/modules/focus/{module_id}"
    module_root.mkdir(parents=True)
    (module_root / "def.txt").write_text(f"focus = {{ id = {module_id} }}\n", encoding="utf-8")
    (root / "paradev.yaml").write_text(
        "\n".join(
            (
                f"project_id: {project_id}",
                f"title: {project_id}",
                "game: hoi4",
                "source_roots: [src]",
                f"output_root: {output_root}",
                "build_root: .paradev/.cache/build",
                "",
            )
        ),
        encoding="utf-8",
    )
    return Project.load(root)
