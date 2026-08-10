from __future__ import annotations

from pathlib import Path

import pytest

from paradev.build.manifest import artifact_module_ids
from paradev.sdk import Project


def _write_project(root: Path) -> Project:
    (root / "paradev.yaml").write_text(
        "\n".join(
            (
                "project_id: module_activity",
                "title: Module Activity",
                "game: hoi4",
                "source_roots: [src]",
                "output_root: output",
                "build_root: build",
                "families:",
                "  bulletin:",
                "    source_slots:",
                "      - name: body",
                "        match: body.txt",
                "        kind: pdx",
                "    templates:",
                "      pdx: events/{object_id}.txt",
                "",
            )
        ),
        encoding="utf-8",
    )
    module_root = root / "src/modules/bulletin/NEWS - Daily News"
    module_root.mkdir(parents=True)
    (module_root / "body.txt").write_text("news = {}\n", encoding="utf-8")
    return Project.load(root)


def test_module_activity_round_trip_keeps_inactive_module_authorable(
    tmp_path: Path,
) -> None:
    project = _write_project(tmp_path)
    metadata_path = tmp_path / "src/modules/bulletin/NEWS - Daily News/meta.yaml"

    plan = project.set_module_active("bulletin/NEWS", False)
    repeated = project.set_module_active("bulletin/NEWS", False)

    assert plan["schema"] == "paradev.sdk.module_activity_update.v1"
    assert plan["previous_active"] is True
    assert plan["active"] is False
    assert plan["changed"] is True
    assert plan["blocked"] is False
    assert plan["plan_hash"] == repeated["plan_hash"]
    assert not metadata_path.exists()

    deactivated = project.set_module_active(
        "bulletin/NEWS",
        False,
        write=True,
        plan_hash=str(plan["plan_hash"]),
    )

    assert deactivated["status"] == "updated"
    assert deactivated["written"] is True
    assert metadata_path.read_text(encoding="utf-8") == "inactive: true\n"
    inactive_project = Project.load(tmp_path)
    inactive_results = (
        inactive_project.build(full_rebuild=True),
        inactive_project.build(),
        inactive_project.build(family="bulletin"),
    )
    assert all(result.modules == () for result in inactive_results)
    assert all("bulletin/NEWS" not in artifact_module_ids(artifact.to_dict()) for result in inactive_results for artifact in result.artifacts)
    with pytest.raises(ValueError, match="is inactive.*module-partial build"):
        inactive_project.build(module_id="bulletin/NEWS")

    browser = Project.load(tmp_path).browser(family="bulletin")
    module_items = [row for row in browser["items"] if row["kind"] == "module"]
    assert [(row["module_id"], row["active"]) for row in module_items] == [("bulletin/NEWS", False)]
    summary_family = next(row for row in Project.load(tmp_path).browser_summary()["families"] if row["family"] == "bulletin")
    assert summary_family["item_count"] == len(module_items)

    activate_plan = Project.load(tmp_path).set_module_active("bulletin/NEWS", True)
    activated = Project.load(tmp_path).set_module_active(
        "bulletin/NEWS",
        True,
        write=True,
        plan_hash=str(activate_plan["plan_hash"]),
    )

    assert activated["status"] == "updated"
    assert activated["active"] is True
    assert not metadata_path.exists()
    assert [module.module_id for module in Project.load(tmp_path).build().modules] == ["bulletin/NEWS"]


def test_module_activity_rejects_stale_plan_without_writing(tmp_path: Path) -> None:
    project = _write_project(tmp_path)
    metadata_path = tmp_path / "src/modules/bulletin/NEWS - Daily News/meta.yaml"
    plan = project.set_module_active("bulletin/NEWS", False)
    metadata_path.write_text("comment: Changed after planning\n", encoding="utf-8")

    stale = project.set_module_active(
        "bulletin/NEWS",
        False,
        write=True,
        plan_hash=str(plan["plan_hash"]),
    )

    assert stale["status"] == "blocked"
    assert stale["written"] is False
    assert stale["diagnostics"][0]["code"] == ("module_activity_update.plan_hash_mismatch")
    assert metadata_path.read_text(encoding="utf-8") == ("comment: Changed after planning\n")


def test_module_activity_migrates_hidden_state_to_visible_metadata(
    tmp_path: Path,
) -> None:
    project = _write_project(tmp_path)
    module_root = tmp_path / "src/modules/bulletin/NEWS - Daily News"
    hidden_path = module_root / ".paradev/meta.yaml"
    hidden_path.parent.mkdir()
    hidden_path.write_text(
        "inactive: true\nsettings:\n  display: compact\n",
        encoding="utf-8",
    )
    project = Project.load(tmp_path)

    plan = project.set_module_active("bulletin/NEWS", False)
    result = project.set_module_active(
        "bulletin/NEWS",
        False,
        write=True,
        plan_hash=str(plan["plan_hash"]),
    )

    assert result["status"] == "updated"
    assert (module_root / "meta.yaml").read_text(encoding="utf-8") == ("inactive: true\n")
    assert hidden_path.read_text(encoding="utf-8") == ("settings:\n  display: compact\n")
