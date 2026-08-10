from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest

import paradev.sdk._module_copy as module_copy
import paradev.sdk.project as project_sdk
from paradev.sdk import Project


def _starter_module(project: Project) -> Path:
    return project.source_roots[0] / "modules/modifier/starter_starter_modifier"


def test_duplicate_module_plans_and_applies_literal_binary_tree(
    tmp_path: Path,
) -> None:
    project = Project.create(tmp_path / "starter")
    source = _starter_module(project)
    binary = b"\x00\xffParaDev\x00\x80"
    (source / "assets/icons").mkdir(parents=True)
    (source / "assets/icons/icon.bin").write_bytes(binary)
    (source / ".paradev").mkdir()
    (source / ".paradev/import.json").write_bytes(b"system provenance")
    (source / ".paradev/meta.yaml").write_text(
        "collection: shared_group\n",
        encoding="utf-8",
    )

    plan = project.duplicate_module(
        "modifier/starter_starter_modifier",
        "starter_copy",
        identity="preserve",
    )
    repeated = project.duplicate_module(
        "modifier/starter_starter_modifier",
        "starter_copy",
        identity="preserve",
    )

    assert plan["schema"] == "paradev.sdk.module_duplicate.v1"
    assert plan["source_module_id"] == ("modifier/starter_starter_modifier")
    assert plan["module_id"] == "modifier/starter_copy"
    assert plan["root"] == str(project.source_roots[0] / "modules/modifier/starter_copy")
    assert plan["relative_path"] == "src/modules/modifier/starter_copy"
    assert plan["status"] == "planned"
    assert plan["blocked"] is False
    assert plan["applied"] is False
    assert plan["written"] is False
    assert plan["content_rewritten"] is False
    assert len(plan["plan_hash"]) == 64
    assert repeated["plan_hash"] == plan["plan_hash"]
    assert plan["totals"] == {
        "directory_count": 4,
        "file_count": 5,
        "excluded_count": 1,
        "size_bytes": sum(path.stat().st_size for path in source.rglob("*") if path.is_file() and path.name != "import.json"),
        "target_size_bytes": sum(path.stat().st_size for path in source.rglob("*") if path.is_file() and path.name != "import.json"),
        "rewritten_file_count": 0,
        "renamed_path_count": 0,
    }
    assert [row["relative_path"] for row in plan["directories"]] == [
        ".",
        ".paradev",
        "assets",
        "assets/icons",
    ]
    binary_row = next(row for row in plan["files"] if row["relative_path"] == "assets/icons/icon.bin")
    assert binary_row["size_bytes"] == len(binary)
    assert len(binary_row["sha256"]) == 64
    assert plan["exclusions"] == [
        {
            "relative_path": ".paradev/import.json",
            "kind": "file",
            "identity": plan["exclusions"][0]["identity"],
            "mode": plan["exclusions"][0]["mode"],
            "mtime_ns": plan["exclusions"][0]["mtime_ns"],
            "reason": "module_local_system_tree",
            "action": "exclude",
        }
    ]
    assert plan["source"]["tree_digest"]
    assert plan["source"]["content_digest"]
    assert plan["destination"]["target_identity"] is None

    applied = project.duplicate_module(
        "modifier/starter_starter_modifier",
        "starter_copy",
        identity="preserve",
        write=True,
        plan_hash=plan["plan_hash"],
    )

    target = project.source_roots[0] / "modules/modifier/starter_copy"
    assert applied["status"] == "duplicated"
    assert applied["blocked"] is False
    assert applied["applied"] is True
    assert applied["written"] is True
    assert applied["plan_hash"] == plan["plan_hash"]
    assert applied["content_rewritten"] is False
    assert applied["destination"]["target_identity"]
    assert (target / "assets/icons/icon.bin").read_bytes() == binary
    assert (target / "def.txt").read_bytes() == (source / "def.txt").read_bytes()
    assert (target / ".paradev/meta.yaml").read_text(encoding="utf-8") == ("collection: shared_group\n")
    assert not (target / ".paradev/import.json").exists()


def test_duplicate_module_excludes_system_tree_without_durable_metadata(
    tmp_path: Path,
) -> None:
    project = Project.create(tmp_path / "starter")
    source = _starter_module(project)
    (source / ".paradev").mkdir()
    (source / ".paradev/import.json").write_bytes(b"system provenance")

    plan = project.duplicate_module(
        "modifier/starter_starter_modifier",
        "starter_copy",
        identity="preserve",
    )

    assert [row["relative_path"] for row in plan["exclusions"]] == [".paradev"]

    applied = project.duplicate_module(
        "modifier/starter_starter_modifier",
        "starter_copy",
        identity="preserve",
        write=True,
        plan_hash=plan["plan_hash"],
    )

    assert applied["status"] == "duplicated"
    assert not (project.source_roots[0] / "modules/modifier/starter_copy/.paradev").exists()


def test_duplicate_module_rewrites_owned_identity_paths_and_text_by_default(
    tmp_path: Path,
) -> None:
    project = Project.create(tmp_path / "starter")
    source = _starter_module(project)
    titled_source = source.with_name("starter_starter_modifier - Starter Modifier")
    source.rename(titled_source)
    (titled_source / "main.loc").write_text(
        "[en.starter_starter_modifier]\n" "Starter Modifier\n\n" "[en.starter_starter_modifier_DESC]\n" "Uses GFX_starter_starter_modifier.\n",
        encoding="utf-8",
    )
    (titled_source / "gfx/starter_starter_modifier").mkdir(parents=True)
    (titled_source / "gfx/starter_starter_modifier/icon.bin").write_bytes(b"starter_starter_modifier\x00\xff")
    (titled_source / "gfx/GFX_starter_starter_modifier.gfx").write_text(
        "spriteType = { name = GFX_starter_starter_modifier }\n",
        encoding="utf-8",
    )

    plan = project.duplicate_module(
        "modifier/starter_starter_modifier",
        "starter_copy",
    )

    target = project.source_roots[0] / "modules/modifier/starter_copy - Starter Modifier"
    assert plan["identity_mode"] == "rewrite"
    assert plan["identity_rewriter"] == "paradev.token-identity.v1"
    assert plan["content_rewritten"] is True
    assert plan["paths_rewritten"] is True
    assert plan["root"] == str(target)
    assert plan["totals"]["rewritten_file_count"] >= 3
    assert plan["totals"]["renamed_path_count"] == 3
    rewritten_gfx = next(row for row in plan["files"] if row["relative_path"] == "gfx/GFX_starter_starter_modifier.gfx")
    assert rewritten_gfx["target_relative_path"] == "gfx/GFX_starter_copy.gfx"
    assert rewritten_gfx["action"] == "rewrite_and_rename"
    binary = next(row for row in plan["files"] if row["relative_path"] == "gfx/starter_starter_modifier/icon.bin")
    assert binary["target_relative_path"] == "gfx/starter_copy/icon.bin"
    assert binary["content_rewritten"] is False
    assert binary["action"] == "rename"

    applied = project.duplicate_module(
        "modifier/starter_starter_modifier",
        "starter_copy",
        write=True,
        plan_hash=plan["plan_hash"],
    )

    assert applied["written"] is True
    assert "starter_copy" in (target / "def.txt").read_text(encoding="utf-8")
    localization = (target / "main.loc").read_text(encoding="utf-8")
    assert "[en.starter_copy]" in localization
    assert "[en.starter_copy_DESC]" in localization
    assert "GFX_starter_copy" in localization
    assert (target / "gfx/GFX_starter_copy.gfx").read_text(encoding="utf-8") == ("spriteType = { name = GFX_starter_copy }\n")
    assert (target / "gfx/starter_copy/icon.bin").read_bytes() == (b"starter_starter_modifier\x00\xff")


def test_duplicate_module_requires_current_plan_hash(
    tmp_path: Path,
) -> None:
    project = Project.create(tmp_path / "starter")
    source = _starter_module(project)
    plan = project.duplicate_module(
        "modifier/starter_starter_modifier",
        "starter_copy",
    )

    missing = project.duplicate_module(
        "modifier/starter_starter_modifier",
        "starter_copy",
        write=True,
    )
    assert missing["status"] == "blocked"
    assert {row["code"] for row in missing["diagnostics"]} == {"module_duplicate.plan_hash_required"}

    (source / "def.txt").write_bytes((source / "def.txt").read_bytes() + b"\n# changed\n")
    stale = project.duplicate_module(
        "modifier/starter_starter_modifier",
        "starter_copy",
        write=True,
        plan_hash=plan["plan_hash"],
    )

    assert stale["status"] == "blocked"
    assert stale["written"] is False
    assert stale["plan_hash"] != plan["plan_hash"]
    assert {row["code"] for row in stale["diagnostics"]} == {"module_duplicate.plan_hash_mismatch"}
    assert not (project.source_roots[0] / "modules/modifier/starter_copy").exists()


def test_duplicate_module_rejects_source_path_swap_during_install(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = Project.create(tmp_path / "starter")
    source = _starter_module(project)
    replacement = source.parent / "swap_candidate"
    replacement.mkdir()
    plan = project.duplicate_module(
        "modifier/starter_starter_modifier",
        "starter_copy",
    )
    original_stage = module_copy._stage_source_file
    swapped = False

    def stage_then_swap(
        source_module_fd: int,
        transaction_fd: int,
        expected: module_copy.ModuleCopyFile,
        *,
        target: module_copy.ModuleCopyTargetFile,
        context: module_copy.ModuleIdentityContext,
        identity_rewriter: module_copy.ModuleIdentityRewriter | None,
        stage_name: str,
        source_path: Path,
    ) -> module_copy._StageFile:
        nonlocal swapped
        staged = original_stage(
            source_module_fd,
            transaction_fd,
            expected,
            target=target,
            context=context,
            identity_rewriter=identity_rewriter,
            stage_name=stage_name,
            source_path=source_path,
        )
        if not swapped:
            detached = source.parent / "swap_detached"
            source.rename(detached)
            replacement.rename(source)
            detached.rename(replacement)
            swapped = True
        return staged

    monkeypatch.setattr(module_copy, "_stage_source_file", stage_then_swap)

    applied = project.duplicate_module(
        "modifier/starter_starter_modifier",
        "starter_copy",
        write=True,
        plan_hash=plan["plan_hash"],
    )

    assert applied["status"] == "blocked"
    assert applied["written"] is False
    assert {row["code"] for row in applied["diagnostics"]} == {"module_duplicate.concurrent_change"}
    assert not (project.source_roots[0] / "modules/modifier/starter_copy").exists()


@pytest.mark.parametrize(
    "folder_name",
    ["starter_copy", "STARTER_COPY - Existing title"],
)
def test_duplicate_module_blocks_exact_and_portable_target_collisions(
    tmp_path: Path,
    folder_name: str,
) -> None:
    project = Project.create(tmp_path / "starter")
    target = project.source_roots[0] / "modules/modifier" / folder_name
    target.mkdir()

    plan = project.duplicate_module(
        "modifier/starter_starter_modifier",
        "starter_copy",
    )

    assert plan["status"] == "blocked"
    assert plan["written"] is False
    assert {row["code"] for row in plan["diagnostics"]} == {"module_duplicate.target_collision"}


def test_duplicate_module_rejects_symlink_special_and_nonportable_entries(
    tmp_path: Path,
) -> None:
    project = Project.create(tmp_path / "starter")
    source = _starter_module(project)
    outside = tmp_path / "outside.bin"
    outside.write_bytes(b"outside")
    (source / "link.bin").symlink_to(outside)

    symlink_plan = project.duplicate_module(
        "modifier/starter_starter_modifier",
        "symlink_copy",
    )
    assert {row["code"] for row in symlink_plan["diagnostics"]} == {"module_duplicate.symlink"}
    (source / "link.bin").unlink()

    (source / ".paradev").mkdir()
    (source / ".paradev/meta.yaml").symlink_to(outside)
    system_symlink_plan = project.duplicate_module(
        "modifier/starter_starter_modifier",
        "system_symlink_copy",
    )
    assert {row["code"] for row in system_symlink_plan["diagnostics"]} == {"module_duplicate.symlink"}
    (source / ".paradev/meta.yaml").unlink()
    (source / ".paradev").rmdir()

    if hasattr(os, "mkfifo"):
        os.mkfifo(source / "pipe")
        special_plan = project.duplicate_module(
            "modifier/starter_starter_modifier",
            "special_copy",
        )
        assert {row["code"] for row in special_plan["diagnostics"]} == {"module_duplicate.special_entry"}
        (source / "pipe").unlink()

    (source / "CON.txt").write_bytes(b"not portable")
    portable_plan = project.duplicate_module(
        "modifier/starter_starter_modifier",
        "portable_copy",
    )
    assert {row["code"] for row in portable_plan["diagnostics"]} == {"module_duplicate.nonportable_name"}


def test_duplicate_module_disambiguates_source_and_destination_roots(
    tmp_path: Path,
) -> None:
    project = Project.create(tmp_path / "starter")
    second_root = project.root / "src-alt"
    duplicate_source = second_root / "modules/modifier/starter_starter_modifier"
    duplicate_source.parent.mkdir(parents=True)
    shutil.copytree(_starter_module(project), duplicate_source)
    manifest = project.manifest_path.read_text(encoding="utf-8")
    project.manifest_path.write_text(
        manifest.replace(
            "source_roots:\n- src\n",
            "source_roots:\n- src\n- src-alt\n",
        ),
        encoding="utf-8",
    )
    project = Project.load(project.root)

    with pytest.raises(
        ValueError,
        match="exists in multiple source roots",
    ):
        project.duplicate_module(
            "modifier/starter_starter_modifier",
            "starter_copy",
        )

    plan = project.duplicate_module(
        "modifier/starter_starter_modifier",
        "starter_copy",
        source_root="src",
        destination_source_root="src-alt",
    )
    applied = project.duplicate_module(
        "modifier/starter_starter_modifier",
        "starter_copy",
        source_root="src",
        destination_source_root="src-alt",
        write=True,
        plan_hash=plan["plan_hash"],
    )

    assert plan["source_root"] == str(project.root / "src")
    assert plan["destination_source_root"] == str(second_root)
    assert applied["written"] is True
    assert b"starter_copy" in (second_root / "modules/modifier/starter_copy/def.txt").read_bytes()
    assert applied["content_rewritten"] is True


def test_duplicate_module_rolls_back_failed_install(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = Project.create(tmp_path / "starter")
    plan = project.duplicate_module(
        "modifier/starter_starter_modifier",
        "starter_copy",
    )
    original_link = module_copy._link_stage_file
    link_count = 0

    def fail_second_link(
        transaction_fd: int,
        stage_name: str,
        target_parent_fd: int,
        target_name: str,
    ) -> None:
        nonlocal link_count
        link_count += 1
        if link_count == 2:
            raise OSError("injected duplicate install failure")
        original_link(
            transaction_fd,
            stage_name,
            target_parent_fd,
            target_name,
        )

    monkeypatch.setattr(module_copy, "_link_stage_file", fail_second_link)

    applied = project.duplicate_module(
        "modifier/starter_starter_modifier",
        "starter_copy",
        write=True,
        plan_hash=plan["plan_hash"],
    )

    assert applied["status"] == "blocked"
    assert applied["written"] is False
    assert {row["code"] for row in applied["diagnostics"]} == {"module_duplicate.concurrent_change"}
    assert not (project.source_roots[0] / "modules/modifier/starter_copy").exists()
    transactions = project.source_roots[0] / ".paradev/module-transactions"
    assert not transactions.exists() or list(transactions.iterdir()) == []


def test_duplicate_module_preserves_changed_target_for_recovery(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = Project.create(tmp_path / "starter")
    plan = project.duplicate_module(
        "modifier/starter_starter_modifier",
        "starter_copy",
    )
    original_link = module_copy._link_stage_file
    first_target: tuple[int, str] | None = None
    link_count = 0

    def change_first_then_fail(
        transaction_fd: int,
        stage_name: str,
        target_parent_fd: int,
        target_name: str,
    ) -> None:
        nonlocal first_target, link_count
        link_count += 1
        if link_count == 1:
            original_link(
                transaction_fd,
                stage_name,
                target_parent_fd,
                target_name,
            )
            first_target = (target_parent_fd, target_name)
            return
        assert first_target is not None
        changed_fd = os.open(
            first_target[1],
            os.O_WRONLY | os.O_TRUNC,
            dir_fd=first_target[0],
        )
        try:
            os.write(changed_fd, b"concurrent user data")
        finally:
            os.close(changed_fd)
        raise OSError("injected failure after concurrent target edit")

    monkeypatch.setattr(
        module_copy,
        "_link_stage_file",
        change_first_then_fail,
    )

    applied = project.duplicate_module(
        "modifier/starter_starter_modifier",
        "starter_copy",
        write=True,
        plan_hash=plan["plan_hash"],
    )

    assert {row["code"] for row in applied["diagnostics"]} == {"module_duplicate.rollback_incomplete"}
    diagnostic = applied["diagnostics"][0]
    recovery_root = Path(diagnostic["recovery_path"])
    assert recovery_root.is_dir()
    assert any(path.read_bytes() == b"concurrent user data" for path in recovery_root.rglob("*") if path.is_file())
    assert not (project.source_roots[0] / "modules/modifier/starter_copy").exists()


def test_duplicate_module_reports_cleanup_pending_after_successful_commit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = Project.create(tmp_path / "starter")
    plan = project.duplicate_module(
        "modifier/starter_starter_modifier",
        "starter_copy",
    )

    def fail_cleanup(
        transactions_fd: int,
        transaction_name: str,
        expected_identity: tuple[int, int],
    ) -> None:
        raise OSError("injected transaction cleanup failure")

    monkeypatch.setattr(module_copy, "_remove_transaction", fail_cleanup)

    applied = project.duplicate_module(
        "modifier/starter_starter_modifier",
        "starter_copy",
        write=True,
        plan_hash=plan["plan_hash"],
    )

    assert applied["status"] == "duplicated"
    assert applied["blocked"] is False
    assert applied["written"] is True
    assert {row["code"] for row in applied["diagnostics"]} == {"module_duplicate.cleanup_pending"}
    assert applied["diagnostics"][0]["severity"] == "warning"
    assert Path(applied["diagnostics"][0]["recovery_path"]).is_dir()
    assert (project.source_roots[0] / "modules/modifier/starter_copy").is_dir()


def test_duplicate_module_fails_closed_when_authority_is_unavailable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = Project.create(tmp_path / "starter")
    monkeypatch.setattr(
        module_copy,
        "_ANCHORED_MODULE_COPY_SUPPORTED",
        False,
    )

    plan = project.duplicate_module(
        "modifier/starter_starter_modifier",
        "starter_copy",
    )

    assert plan["status"] == "blocked"
    assert plan["directories"] == []
    assert plan["files"] == []
    assert {row["code"] for row in plan["diagnostics"]} == {"module_duplicate.unsupported_platform"}


def test_duplicate_module_holds_source_mutation_lock_through_commit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = Project.create(tmp_path / "starter")
    plan = project.duplicate_module(
        "modifier/starter_starter_modifier",
        "starter_copy",
    )
    original_install = module_copy.install_module_copy
    lock_active = False
    installed_under_lock = False

    @project_sdk.contextmanager
    def tracking_lock(locked_project: Project):
        nonlocal lock_active
        assert locked_project is project
        lock_active = True
        try:
            yield
        finally:
            lock_active = False

    def tracking_install(*args: object, **kwargs: object):
        nonlocal installed_under_lock
        installed_under_lock = lock_active
        return original_install(*args, **kwargs)

    monkeypatch.setattr(
        project_sdk,
        "_project_source_mutation_lock",
        tracking_lock,
    )
    monkeypatch.setattr(
        module_copy,
        "install_module_copy",
        tracking_install,
    )

    applied = project.duplicate_module(
        "modifier/starter_starter_modifier",
        "starter_copy",
        write=True,
        plan_hash=plan["plan_hash"],
    )

    assert applied["written"] is True
    assert installed_under_lock is True
    assert lock_active is False
