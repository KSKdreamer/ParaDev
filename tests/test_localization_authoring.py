from __future__ import annotations

from pathlib import Path

import pytest

from paradev.sdk import Project


def _idea_project(tmp_path: Path, text: str) -> tuple[Project, Path]:
    project = Project.create(
        tmp_path / "localization-authoring",
        project_id="localization_authoring",
        title="Localization Authoring",
    )
    module_root = project.root / "src/modules/idea/IDEA_TEST"
    module_root.mkdir(parents=True, exist_ok=True)
    (module_root / "def.txt").write_text("IDEA_TEST = { }\n", encoding="utf-8")
    source_path = module_root / "main.loc"
    source_path.write_bytes(text.encode("utf-8"))
    return project, source_path


def test_project_localization_workspace_and_planner_are_lossless_no_write_operations(
    tmp_path: Path,
) -> None:
    source_text = "[en.IDEA_TEST]\r\n" "Old title\r\n" "\r\n" "[zh.IDEA_TEST]\r\n" "旧标题\r\n"
    project, source_path = _idea_project(tmp_path, source_text)

    workspace = project.localization_workspace("idea/IDEA_TEST")

    assert workspace["schema"] == "paradev.localization-workspace.v2"
    assert workspace["target"] == {
        "kind": "module",
        "id": "idea/IDEA_TEST",
        "family": "idea",
        "object_id": "IDEA_TEST",
    }
    assert workspace["languages"] == ["l_english", "l_simp_chinese"]
    assert workspace["coverage"] == {
        "truncated": False,
        "shown_rows": 1,
        "total_rows": 1,
    }
    assert workspace["rows"][0]["values"]["l_english"]["text"] == "Old title"

    plan = project.plan_localization_update(
        "idea/IDEA_TEST",
        {"op": "set", "language": "en", "key": "IDEA_TEST", "value": "New title"},
    )

    assert plan["schema"] == "paradev.localization-update-plan.v2"
    assert plan["changed"] is True
    assert plan["source_edits"][0]["text"] == source_text.replace("Old title", "New title")
    assert source_path.read_bytes() == source_text.encode("utf-8")

    applied = project.apply_source_draft(source_edits=plan["source_edits"])

    assert applied["written"] is True
    assert source_path.read_bytes() == source_text.replace("Old title", "New title").encode("utf-8")


def test_project_localization_add_rename_remove_chain_uses_unsaved_drafts(
    tmp_path: Path,
) -> None:
    project, source_path = _idea_project(
        tmp_path,
        "[en.IDEA_TEST]\nTitle\n\n[zh.IDEA_TEST]\n标题\n",
    )

    added = project.plan_localization_update("idea/IDEA_TEST", {"op": "add"})
    added_text = added["source_edits"][0]["text"]

    assert added["operation"] == {
        "op": "add",
        "key": "IDEA_TEST_NEW",
        "languages": ["l_english", "l_simp_chinese"],
    }
    assert {row["key"] for row in added["workspace"]["rows"]} == {
        "IDEA_TEST",
        "IDEA_TEST_NEW",
    }
    assert source_path.read_text(encoding="utf-8") == "[en.IDEA_TEST]\nTitle\n\n[zh.IDEA_TEST]\n标题\n"

    renamed = project.plan_localization_update(
        "idea/IDEA_TEST",
        {"op": "rename", "key": "IDEA_TEST_NEW", "new_key": "@DESC"},
        drafts={str(source_path): added_text},
    )
    renamed_text = renamed["source_edits"][0]["text"]

    assert renamed["operation"]["new_key"] == "IDEA_TEST_DESC"
    assert "[en.IDEA_TEST_DESC]" in renamed_text
    assert "[zh.IDEA_TEST_DESC]" in renamed_text

    removed = project.plan_localization_update(
        "idea/IDEA_TEST",
        {"op": "remove", "key": "IDEA_TEST_DESC"},
        drafts={"src/modules/idea/IDEA_TEST/main.loc": renamed_text},
    )

    assert [row["key"] for row in removed["workspace"]["rows"]] == ["IDEA_TEST"]
    assert "IDEA_TEST_DESC" not in removed["source_edits"][0]["text"]


def test_project_localization_planner_rejects_collisions_and_foreign_drafts(
    tmp_path: Path,
) -> None:
    project, _source_path = _idea_project(
        tmp_path,
        "[en.IDEA_TEST]\nTitle\n\n[en.IDEA_TEST_DESC]\nDescription\n",
    )
    foreign = project.root / "README.md"
    foreign.write_text("not localization", encoding="utf-8")

    with pytest.raises(ValueError, match="already exists"):
        project.plan_localization_update(
            "idea/IDEA_TEST",
            {"op": "rename", "key": "IDEA_TEST", "new_key": "IDEA_TEST_DESC"},
        )
    with pytest.raises(ValueError, match="not owned by module"):
        project.localization_workspace(
            "idea/IDEA_TEST",
            drafts={str(foreign): "changed"},
        )


def test_project_localization_workspace_keeps_empty_sections_editable(
    tmp_path: Path,
) -> None:
    project, _source_path = _idea_project(
        tmp_path,
        "[en.IDEA_TEST]\n\n[en.IDEA_TEST_DESC]\nDescription\n",
    )

    plan = project.plan_localization_update(
        "idea/IDEA_TEST",
        {"op": "set", "language": "en", "key": "IDEA_TEST", "value": "Filled"},
    )

    assert plan["source_edits"][0]["text"] == ("[en.IDEA_TEST]\nFilled\n[en.IDEA_TEST_DESC]\nDescription\n")


def test_project_localization_planner_edits_apostrophe_keys(
    tmp_path: Path,
) -> None:
    project, _source_path = _idea_project(
        tmp_path,
        "[en.IDEA_ISN'T_OVER]\nOld title\n",
    )

    plan = project.plan_localization_update(
        "idea/IDEA_TEST",
        {
            "op": "set",
            "language": "en",
            "key": "IDEA_ISN'T_OVER",
            "value": "New title",
        },
    )

    assert plan["source_edits"][0]["text"] == ("[en.IDEA_ISN'T_OVER]\nNew title\n")


def test_project_collection_localization_uses_the_same_guarded_workspace(
    tmp_path: Path,
) -> None:
    project = Project.create(
        tmp_path / "collection-localization-authoring",
        project_id="collection_localization_authoring",
        title="Collection Localization Authoring",
    )
    collection_root = project.root / "src/collections/decision/DECISION_CATEGORY_TEST - Test category"
    collection_root.mkdir(parents=True)
    (collection_root / "def.txt").write_text(
        "DECISION_CATEGORY_TEST = { }\n",
        encoding="utf-8",
    )
    source_path = collection_root / "main.loc"
    source_path.write_text(
        "[en.DECISION_CATEGORY_TEST]\nOld category\n",
        encoding="utf-8",
    )

    workspace = project.localization_workspace(
        "DECISION_CATEGORY_TEST",
        target_kind="collection",
        family="decision",
    )

    assert workspace["target"] == {
        "kind": "collection",
        "id": "DECISION_CATEGORY_TEST",
        "family": "decision",
        "object_id": "DECISION_CATEGORY_TEST",
    }
    assert workspace["sources"][0]["unit_relative_path"] == "main.loc"

    plan = project.plan_localization_update(
        "DECISION_CATEGORY_TEST",
        {
            "op": "set",
            "language": "en",
            "key": "DECISION_CATEGORY_TEST",
            "value": "New category",
        },
        target_kind="collection",
        family="decision",
    )

    assert plan["target"] == workspace["target"]
    assert plan["source_edits"][0]["text"] == ("[en.DECISION_CATEGORY_TEST]\nNew category\n")
    assert source_path.read_text(encoding="utf-8") == ("[en.DECISION_CATEGORY_TEST]\nOld category\n")
