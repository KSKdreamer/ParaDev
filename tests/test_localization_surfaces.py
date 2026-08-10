from __future__ import annotations

from pathlib import Path

import pytest

from paradev.sdk import Project, get_frontend_api_contract
from paradev.surfaces.mcp import create_authoring_mcp_toolkit
from paradev.surfaces.rest import (
    LOCALIZATION_PLAN_PATH,
    LOCALIZATION_WORKSPACE_PATH,
    build_app,
    get_openapi_seed,
)


def _multi_source_idea_project(tmp_path: Path) -> tuple[Project, Path, Path]:
    project = Project.create(
        tmp_path / "localization-surfaces",
        project_id="localization_surfaces",
        title="Localization Surfaces",
    )
    module_root = project.root / "src/modules/idea/IDEA_MULTI"
    module_root.mkdir(parents=True, exist_ok=True)
    (module_root / "def.txt").write_text("IDEA_MULTI = { }\n", encoding="utf-8")
    title_path = module_root / "title.loc"
    title_path.write_text(
        "[en.IDEA_MULTI]\nOld title\n\n[zh.IDEA_MULTI]\n旧标题\n",
        encoding="utf-8",
    )
    description_path = module_root / "description.loc"
    description_path.write_text(
        "[en.IDEA_MULTI_desc]\nOld description\n\n[zh.IDEA_MULTI_desc]\n旧描述\n",
        encoding="utf-8",
    )
    return project, title_path, description_path


def _decision_collection_project(tmp_path: Path) -> tuple[Project, Path]:
    project = Project.create(
        tmp_path / "collection-localization-surfaces",
        project_id="collection_localization_surfaces",
        title="Collection Localization Surfaces",
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
    return project, source_path


def _surface_path(template: str, project_id: str) -> str:
    return template.replace("{project_id}", project_id)


def test_localization_frontend_contract_binds_project_rest_and_mcp() -> None:
    rows = {row["id"]: row for row in get_frontend_api_contract()["operations"]}
    seed = get_openapi_seed()

    workspace = rows["localization.workspace"]
    plan = rows["localization.plan"]

    assert workspace["bindings"] == {
        "sdk": {"call": "Project.localization_workspace"},
        "rest": {
            "method": "POST",
            "path": LOCALIZATION_WORKSPACE_PATH,
            "query": {},
        },
        "mcp": {"tool": "localization_workspace"},
    }
    assert plan["bindings"] == {
        "sdk": {"call": "Project.plan_localization_update"},
        "rest": {"method": "POST", "path": LOCALIZATION_PLAN_PATH, "query": {}},
        "mcp": {"tool": "localization_plan"},
    }
    assert seed["paths"][LOCALIZATION_WORKSPACE_PATH]["post"]["x-paradev-frontend-api-operation-ids"] == ["localization.workspace"]
    assert seed["paths"][LOCALIZATION_PLAN_PATH]["post"]["x-paradev-frontend-api-operation-ids"] == ["localization.plan"]


def test_localization_rest_routes_preserve_multi_file_drafts_and_recover_after_error(
    tmp_path: Path,
) -> None:
    testclient = pytest.importorskip("fastapi.testclient")
    project, title_path, description_path = _multi_source_idea_project(tmp_path)
    client = testclient.TestClient(build_app())
    workspace_path = _surface_path(LOCALIZATION_WORKSPACE_PATH, project.project_id)
    plan_path = _surface_path(LOCALIZATION_PLAN_PATH, project.project_id)
    title_draft = title_path.read_text(encoding="utf-8").replace("Old title", "Unsaved title")
    description_draft = description_path.read_text(encoding="utf-8").replace(
        "Old description",
        "Unsaved description",
    )
    drafts = [
        {"source_path": str(title_path), "text": title_draft},
        {"source_path": str(description_path), "text": description_draft},
    ]

    workspace_response = client.post(
        workspace_path,
        json={
            "project_root": str(project.root),
            "target_kind": "module",
            "target_id": "idea/IDEA_MULTI",
            "drafts": drafts,
        },
    )

    assert workspace_response.status_code == 200, workspace_response.text
    workspace = workspace_response.json()
    assert len(workspace["sources"]) == 2
    rows = {row["key"]: row for row in workspace["rows"]}
    assert rows["IDEA_MULTI"]["values"]["l_english"]["text"] == "Unsaved title"
    assert rows["IDEA_MULTI_desc"]["values"]["l_english"]["text"] == "Unsaved description"

    collision = client.post(
        plan_path,
        json={
            "project_root": str(project.root),
            "target_kind": "module",
            "target_id": "idea/IDEA_MULTI",
            "drafts": drafts,
            "operation": {
                "op": "rename",
                "key": "IDEA_MULTI",
                "new_key": "IDEA_MULTI_desc",
            },
        },
    )
    assert collision.status_code == 400
    assert "already exists" in collision.json()["detail"]

    recovered = client.post(
        plan_path,
        json={
            "project_root": str(project.root),
            "target_kind": "module",
            "target_id": "idea/IDEA_MULTI",
            "drafts": drafts,
            "operation": {
                "op": "set",
                "language": "zh",
                "key": "IDEA_MULTI_desc",
                "value": "新描述",
            },
        },
    )

    assert recovered.status_code == 200, recovered.text
    payload = recovered.json()
    assert payload["changed"] is True
    assert len(payload["source_edits"]) == 1
    assert payload["source_edits"][0]["path"] == str(description_path)
    assert "[zh.IDEA_MULTI_desc]\n新描述" in payload["source_edits"][0]["text"]
    assert title_path.read_text(encoding="utf-8").startswith("[en.IDEA_MULTI]\nOld title")
    assert description_path.read_text(encoding="utf-8").startswith("[en.IDEA_MULTI_desc]\nOld description")


def test_localization_mcp_tools_share_closed_schemas_and_plan_without_writing(
    tmp_path: Path,
) -> None:
    project, title_path, description_path = _multi_source_idea_project(tmp_path)
    toolkit = create_authoring_mcp_toolkit()
    workspace_tool = toolkit.tools["localization_workspace"]
    plan_tool = toolkit.tools["localization_plan"]

    assert workspace_tool.input_schema["required"] == [
        "path",
        "target_kind",
        "target_id",
    ]
    assert plan_tool.input_schema["required"] == [
        "path",
        "target_kind",
        "target_id",
        "operation",
    ]
    operation_schema = plan_tool.input_schema["properties"]["operation"]
    assert [row["properties"]["op"]["const"] for row in operation_schema["oneOf"]] == [
        "set",
        "add",
        "rename",
        "remove",
    ]

    workspace = toolkit.run(
        "localization_workspace",
        path=str(project.root),
        target_kind="module",
        target_id="idea/IDEA_MULTI",
    )
    plan = toolkit.run(
        "localization_plan",
        path=str(project.root),
        target_kind="module",
        target_id="idea/IDEA_MULTI",
        operation={
            "op": "set",
            "language": "en",
            "key": "IDEA_MULTI_desc",
            "value": "New description",
        },
    )

    assert len(workspace["sources"]) == 2
    assert len(plan["source_edits"]) == 1
    assert plan["source_edits"][0]["path"] == str(description_path)
    assert title_path.read_text(encoding="utf-8").endswith("[zh.IDEA_MULTI]\n旧标题\n")
    assert "Old description" in description_path.read_text(encoding="utf-8")


def test_collection_localization_is_first_class_over_rest_and_mcp(
    tmp_path: Path,
) -> None:
    testclient = pytest.importorskip("fastapi.testclient")
    project, source_path = _decision_collection_project(tmp_path)
    client = testclient.TestClient(build_app())

    response = client.post(
        _surface_path(LOCALIZATION_WORKSPACE_PATH, project.project_id),
        json={
            "project_root": str(project.root),
            "target_kind": "collection",
            "target_id": "DECISION_CATEGORY_TEST",
            "family": "decision",
        },
    )

    assert response.status_code == 200, response.text
    workspace = response.json()
    assert workspace["target"] == {
        "kind": "collection",
        "id": "DECISION_CATEGORY_TEST",
        "family": "decision",
        "object_id": "DECISION_CATEGORY_TEST",
    }
    assert workspace["sources"][0]["unit_relative_path"] == "main.loc"

    toolkit = create_authoring_mcp_toolkit()
    plan = toolkit.run(
        "localization_plan",
        path=str(project.root),
        target_kind="collection",
        target_id="DECISION_CATEGORY_TEST",
        family="decision",
        operation={
            "op": "set",
            "language": "en",
            "key": "DECISION_CATEGORY_TEST",
            "value": "New category",
        },
    )

    assert plan["target"] == workspace["target"]
    assert plan["source_edits"][0]["text"] == ("[en.DECISION_CATEGORY_TEST]\nNew category\n")
    assert source_path.read_text(encoding="utf-8") == ("[en.DECISION_CATEGORY_TEST]\nOld category\n")
