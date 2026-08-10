from __future__ import annotations

import pytest
from heavenbase.utils import dumps_json, loads_json
from typer.testing import CliRunner

from paradev.cli import build_app as build_cli_app
from paradev.sdk import (
    Project,
    get_frontend_api_form,
    get_frontend_api_operation,
    get_project_api_table,
    normalize_frontend_api_inputs,
    plan_frontend_api_rest_request,
)
from paradev.sdk._module_diagram_api import (
    MAX_MODULE_DIAGRAM_EDGE_INTENTS,
    MAX_MODULE_DIAGRAM_NODE_INTENTS,
    MAX_MODULE_DIAGRAM_POSITION_INTENTS,
)
from paradev.surfaces.cli import get_cli_api_table
from paradev.surfaces.mcp import create_authoring_mcp_toolkit, get_mcp_api_table
from paradev.surfaces.rest import (
    MODULE_DIAGRAM_EDIT_PATH,
    MODULE_DIAGRAM_PATH,
    edit_module_diagram,
    get_openapi_seed,
    get_rest_api_table,
    read_module_diagram,
)
from paradev.surfaces.rest import (
    build_app as build_rest_app,
)


def _projection(family: str, profile: str | None) -> dict[str, object]:
    return {
        "schema": "paradev.sdk.module_diagram.v1",
        "family": family,
        "profile": profile,
        "editable": True,
        "nodes": [],
        "edges": [],
    }


def _edit_payload(
    family: str,
    *,
    profile: str | None,
    position_intents: object,
    edge_intents: object,
    node_intents: object,
    write: bool,
    plan_hash: str | None,
) -> dict[str, object]:
    return {
        "schema": "paradev.sdk.module_diagram_edit.v1",
        "family": family,
        "profile": profile,
        "position_intents": position_intents,
        "edge_intents": edge_intents,
        "node_intents": node_intents,
        "write": write,
        "plan_hash": plan_hash or "reviewed-plan",
        "status": "applied" if write else "planned",
        "blocked": False,
    }


def _write_focus_tree_surface_project(root) -> Project:
    (root / "paradev.yaml").write_text(
        """project_id: focus_tree_surfaces
title: Focus Tree Surfaces
game: hoi4
source_roots: [src]
output_root: build/mod
build_root: .paradev/.cache/build
families:
  focus_tree:
    source_slots:
      - {name: def, match: def.txt, kind: pdx, required: true}
      - {name: loc, match: '**/*.loc', kind: loc, many: true}
    templates:
      pdx: common/national_focus/{object_id}.txt
      loc: localisation/{language_folder}/{object_id}_{language}.yml
""",
        encoding="utf-8",
    )
    tree = root / "src/modules/focus_tree/TEST_TREE"
    tree.mkdir(parents=True)
    (tree / "def.txt").write_text(
        (
            "focus_tree = {\n"
            "    id = TEST_TREE\n"
            "    focus = {\n"
            "        id = FOCUS_A\n"
            "        x = 0\n"
            "        y = 0\n"
            "    }\n"
            "    focus = {\n"
            "        id = FOCUS_B\n"
            "        prerequisite = {\n"
            "            focus = FOCUS_A\n"
            "        }\n"
            "        x = 1\n"
            "        y = 1\n"
            "    }\n"
            "}\n"
        ),
        encoding="utf-8",
    )
    (tree / "main.loc").write_text(
        (
            "[en.FOCUS_A]\n"
            "Focus A\n\n"
            "[en.FOCUS_A_desc]\n"
            "First Focus description.\n\n"
            "[en.FOCUS_B]\n"
            "Focus B\n\n"
            "[en.FOCUS_B_desc]\n"
            "Second Focus description.\n"
        ),
        encoding="utf-8",
    )
    return Project.load(root)


def test_module_diagram_frontend_contract_plans_matching_rest_requests() -> None:
    projection = get_frontend_api_operation("module.diagram")
    edit = get_frontend_api_operation("module.diagram.edit")
    form = get_frontend_api_form("module.diagram.edit")

    assert projection["bindings"]["rest"] == {
        "method": "GET",
        "path": MODULE_DIAGRAM_PATH,
        "query": {},
    }
    assert edit["bindings"]["rest"] == {
        "method": "POST",
        "path": MODULE_DIAGRAM_EDIT_PATH,
        "query": {},
    }
    properties = form["json_schema"]["properties"]
    assert properties["position_intents"]["maxItems"] == (MAX_MODULE_DIAGRAM_POSITION_INTENTS)
    assert properties["position_intents"]["items"]["type"] == "object"
    assert properties["edge_intents"]["maxItems"] == (MAX_MODULE_DIAGRAM_EDGE_INTENTS)
    assert properties["node_intents"]["maxItems"] == (MAX_MODULE_DIAGRAM_NODE_INTENTS)

    read_plan = plan_frontend_api_rest_request(
        "module.diagram",
        {"path": "/project", "family": "technology", "profile": "hoi4"},
    )
    edit_plan = plan_frontend_api_rest_request(
        "module.diagram.edit",
        {
            "path": "/project",
            "family": "focus_tree",
            "position_intents": [{"focus_id": "A"}],
        },
    )

    assert read_plan["method"] == "GET"
    assert read_plan["path"] == MODULE_DIAGRAM_PATH
    assert read_plan["query"] == {
        "path": "/project",
        "family": "technology",
        "profile": "hoi4",
    }
    assert read_plan["body"] == {}
    assert edit_plan["method"] == "POST"
    assert edit_plan["path"] == MODULE_DIAGRAM_EDIT_PATH
    assert edit_plan["query"] == {}
    assert edit_plan["body"] == {
        "project_root": "/project",
        "family": "focus_tree",
        "position_intents": [{"focus_id": "A"}],
        "edge_intents": [],
        "node_intents": [],
        "write": False,
    }

    with pytest.raises(ValueError, match="cannot contain more than"):
        normalize_frontend_api_inputs(
            "module.diagram.edit",
            {
                "path": "/project",
                "family": "technology",
                "position_intents": [{}] * (MAX_MODULE_DIAGRAM_POSITION_INTENTS + 1),
            },
        )


def test_focus_tree_diagram_real_cli_rest_and_mcp_routes_share_the_sdk_contract(
    tmp_path,
) -> None:
    project = _write_focus_tree_surface_project(tmp_path)
    rest_projection = read_module_diagram(
        path=str(project.root),
        family="focus_trees",
        profile="hoi4",
    )
    focus = next(row for row in rest_projection["nodes"] if row["id"] == "FOCUS_B")
    intents = [
        {
            "focus_id": "FOCUS_B",
            "x": 3,
            "y": 4,
            "source_revision": focus["source_revision"],
        }
    ]
    rest_plan = edit_module_diagram(
        request={
            "project_root": str(project.root),
            "family": "focus_tree",
            "position_intents": intents,
        }
    )

    runner = CliRunner()
    cli_result = runner.invoke(
        build_cli_app(),
        [
            "module-diagram",
            str(project.root),
            "focus_tree",
            "--json",
        ],
    )
    toolkit = create_authoring_mcp_toolkit()
    mcp_projection = toolkit.run(
        "module_diagram",
        path=str(project.root),
        family="focus_tree",
    )
    mcp_plan = toolkit.run(
        "module_diagram_edit",
        path=str(project.root),
        family="focus_trees",
        position_intents=intents,
    )

    assert cli_result.exit_code == 0, cli_result.output
    cli_projection = loads_json(cli_result.output)
    assert rest_projection["provider_schema"] == ("paradev.hoi4.focus-tree-diagram-projection.v1")
    assert cli_projection["provider_schema"] == rest_projection["provider_schema"]
    assert mcp_projection["provider_schema"] == rest_projection["provider_schema"]
    assert rest_plan["status"] == "planned"
    assert mcp_plan["status"] == "planned"
    assert rest_plan["plan_hash"] == mcp_plan["plan_hash"]
    assert rest_plan["drafts"] == mcp_plan["drafts"]
    assert rest_plan["family"] == "focus_tree"
    assert mcp_plan["family"] == "focus_tree"


def test_focus_node_creation_rest_and_mcp_share_guarded_plan_and_apply(
    tmp_path,
) -> None:
    testclient = pytest.importorskip("fastapi.testclient")
    project = _write_focus_tree_surface_project(tmp_path)
    projection = project.module_diagram("focus_tree")
    tree = next(row for row in projection["trees"] if row["id"] == "TEST_TREE")
    request = {
        "tree_id": "TEST_TREE",
        "focus_id": "FOCUS_NEW",
        "x": 2,
        "y": 3,
        "title": "New Focus",
        "description": "A reviewed Focus node.",
        "source_revision": tree["source_revision"],
        "relative_position_id": "FOCUS_A",
        "prerequisite_id": "FOCUS_A",
    }

    rest_plan = edit_module_diagram(
        request={
            "project_root": str(project.root),
            "family": "focus_tree",
            "node_intents": [request],
        }
    )
    route_response = testclient.TestClient(build_rest_app()).post(
        MODULE_DIAGRAM_EDIT_PATH,
        json={
            "project_root": str(project.root),
            "family": "focus_tree",
            "node_intents": [request],
        },
    )
    toolkit = create_authoring_mcp_toolkit()
    mcp_plan = toolkit.run(
        "module_diagram_edit",
        path=str(project.root),
        family="focus_tree",
        node_intents=[request],
    )

    assert rest_plan["provider_schema"] == ("paradev.hoi4.focus-tree-node-creation-plan.v1")
    assert route_response.status_code == 200, route_response.text
    assert route_response.json()["plan_hash"] == rest_plan["plan_hash"]
    assert rest_plan["plan_hash"] == mcp_plan["plan_hash"]
    assert rest_plan["drafts"] == mcp_plan["drafts"]
    assert rest_plan["intent"]["icon_key"] == "GFX_goal_unknown"
    assert rest_plan["absent_file_targets"] == [
        {
            "path": "src/modules/focus_tree/TEST_TREE/icons/FOCUS_NEW.png",
            "kind": "focus_preview_png",
            "content_type": "image/png",
            "precondition": "absent",
            "write": False,
        }
    ]

    applied = toolkit.run(
        "module_diagram_edit",
        path=str(project.root),
        family="focus_tree",
        node_intents=[request],
        write=True,
        plan_hash=rest_plan["plan_hash"],
    )

    assert applied["status"] == "applied"
    assert applied["written"] is True
    assert "icon = GFX_goal_unknown" in (project.root / "src/modules/focus_tree/TEST_TREE/def.txt").read_text(encoding="utf-8")
    assert "[en.FOCUS_NEW]\nNew Focus" in (project.root / "src/modules/focus_tree/TEST_TREE/main.loc").read_text(encoding="utf-8")

    edit_schema = get_openapi_seed()["paths"][MODULE_DIAGRAM_EDIT_PATH]["post"]["requestBody"]["content"]["application/json"]["schema"]
    assert edit_schema["additionalProperties"] is False
    assert edit_schema["required"] == ["project_root", "family"]
    assert edit_schema["properties"]["node_intents"]["maxItems"] == 1
    assert edit_schema["allOf"][0]["then"]["required"] == ["plan_hash"]


def test_module_diagram_rest_helpers_routes_and_openapi_forward_sdk(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    testclient = pytest.importorskip("fastapi.testclient")
    project = Project.create(tmp_path / "starter", title="Starter")
    calls: list[tuple[str, dict[str, object]]] = []

    def project_diagram(
        self: Project,
        family: str,
        *,
        profile: str | None = None,
    ) -> dict[str, object]:
        calls.append(("read", {"family": family, "profile": profile}))
        return _projection(family, profile)

    def project_edit_diagram(
        self: Project,
        family: str,
        *,
        position_intents: object = (),
        edge_intents: object = (),
        node_intents: object = (),
        profile: str | None = None,
        write: bool = False,
        plan_hash: str | None = None,
    ) -> dict[str, object]:
        call = {
            "family": family,
            "profile": profile,
            "position_intents": position_intents,
            "edge_intents": edge_intents,
            "node_intents": node_intents,
            "write": write,
            "plan_hash": plan_hash,
        }
        calls.append(("edit", call))
        return _edit_payload(
            family,
            profile=profile,
            position_intents=position_intents,
            edge_intents=edge_intents,
            node_intents=node_intents,
            write=write,
            plan_hash=plan_hash,
        )

    monkeypatch.setattr(Project, "module_diagram", project_diagram)
    monkeypatch.setattr(Project, "edit_module_diagram", project_edit_diagram)

    direct_read = read_module_diagram(
        path=str(project.root),
        family="mio",
        profile="hoi4",
    )
    direct_node_intents = [
        {
            "organization_id": "ORG",
            "parent_trait_id": "ROOT",
            "trait_id": "CHILD",
            "title": "Child",
        }
    ]
    direct_edit = edit_module_diagram(
        request={
            "project_root": str(project.root),
            "family": "mio",
            "node_intents": direct_node_intents,
        }
    )
    client = testclient.TestClient(build_rest_app())
    read_response = client.get(
        MODULE_DIAGRAM_PATH,
        params={
            "path": str(project.root),
            "family": "mio",
            "profile": "hoi4",
        },
    )
    edit_response = client.post(
        MODULE_DIAGRAM_EDIT_PATH,
        json={
            "project_root": str(project.root),
            "family": "mio",
            "position_intents": [
                {
                    "organization_id": "ORG",
                    "trait_id": "CHILD",
                    "x": 2,
                    "y": 1,
                    "source_revision": "sha256:" + ("a" * 64),
                }
            ],
            "edge_intents": [
                {
                    "kind": kind,
                    "organization_id": "ORG",
                    "source_id": "ROOT",
                    "target_id": "CHILD",
                    "present": True,
                    "source_revision": "sha256:" + ("a" * 64),
                }
                for kind in (
                    "relative_position",
                    "any_parent",
                    "all_parent",
                    "mutually_exclusive",
                )
            ],
            "write": True,
            "plan_hash": "reviewed-plan",
        },
    )

    assert direct_read["schema"] == "paradev.sdk.module_diagram.v1"
    assert direct_edit["status"] == "planned"
    assert read_response.status_code == 200, read_response.text
    assert edit_response.status_code == 200, edit_response.text
    assert edit_response.json()["status"] == "applied"
    assert calls == [
        ("read", {"family": "mio", "profile": "hoi4"}),
        (
            "edit",
            {
                "family": "mio",
                "profile": None,
                "position_intents": [],
                "edge_intents": [],
                "node_intents": direct_node_intents,
                "write": False,
                "plan_hash": None,
            },
        ),
        (
            "read",
            {
                "family": "mio",
                "profile": "hoi4",
            },
        ),
        (
            "edit",
            {
                "family": "mio",
                "profile": None,
                "position_intents": [
                    {
                        "organization_id": "ORG",
                        "trait_id": "CHILD",
                        "x": 2,
                        "y": 1,
                        "source_revision": "sha256:" + ("a" * 64),
                    }
                ],
                "edge_intents": [
                    {
                        "kind": kind,
                        "organization_id": "ORG",
                        "source_id": "ROOT",
                        "target_id": "CHILD",
                        "present": True,
                        "source_revision": "sha256:" + ("a" * 64),
                    }
                    for kind in (
                        "relative_position",
                        "any_parent",
                        "all_parent",
                        "mutually_exclusive",
                    )
                ],
                "node_intents": [],
                "write": True,
                "plan_hash": "reviewed-plan",
            },
        ),
    ]

    seed = get_openapi_seed()
    get_operation = seed["paths"][MODULE_DIAGRAM_PATH]["get"]
    post_operation = seed["paths"][MODULE_DIAGRAM_EDIT_PATH]["post"]
    post_schema = post_operation["requestBody"]["content"]["application/json"]["schema"]
    family_parameter = next(row for row in get_operation["parameters"] if row["name"] == "family")
    assert get_operation["x-paradev-frontend-api-operation-ids"] == ["module.diagram"]
    assert post_operation["x-paradev-frontend-api-operation-ids"] == ["module.diagram.edit"]
    assert family_parameter["schema"]["pattern"] == "^[a-z][a-z0-9_-]*$"
    assert post_schema["required"] == ["project_root", "family"]
    assert post_schema["properties"]["family"]["pattern"] == "^[a-z][a-z0-9_-]*$"
    assert post_schema["properties"]["position_intents"]["maxItems"] == (MAX_MODULE_DIAGRAM_POSITION_INTENTS)
    assert post_schema["properties"]["edge_intents"]["maxItems"] == (MAX_MODULE_DIAGRAM_EDGE_INTENTS)
    assert post_schema["properties"]["node_intents"]["maxItems"] == (MAX_MODULE_DIAGRAM_NODE_INTENTS)
    assert post_schema["properties"]["position_intents"]["items"]["type"] == "object"
    assert post_schema["properties"]["edge_intents"]["items"]["type"] == "object"

    with pytest.raises(ValueError, match="cannot contain more than"):
        edit_module_diagram(
            request={
                "project_root": str(project.root),
                "family": "technology",
                "edge_intents": [{}] * (MAX_MODULE_DIAGRAM_EDGE_INTENTS + 1),
            }
        )


def test_module_diagram_cli_and_mcp_forward_bounded_intents(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = Project.create(tmp_path / "starter", title="Starter")
    calls: list[tuple[str, dict[str, object]]] = []

    def project_diagram(
        self: Project,
        family: str,
        *,
        profile: str | None = None,
    ) -> dict[str, object]:
        calls.append(("read", {"family": family, "profile": profile}))
        return _projection(family, profile)

    def project_edit_diagram(
        self: Project,
        family: str,
        *,
        position_intents: object = (),
        edge_intents: object = (),
        node_intents: object = (),
        profile: str | None = None,
        write: bool = False,
        plan_hash: str | None = None,
    ) -> dict[str, object]:
        call = {
            "family": family,
            "profile": profile,
            "position_intents": position_intents,
            "edge_intents": edge_intents,
            "node_intents": node_intents,
            "write": write,
            "plan_hash": plan_hash,
        }
        calls.append(("edit", call))
        return _edit_payload(
            family,
            profile=profile,
            position_intents=position_intents,
            edge_intents=edge_intents,
            node_intents=node_intents,
            write=write,
            plan_hash=plan_hash,
        )

    monkeypatch.setattr(Project, "module_diagram", project_diagram)
    monkeypatch.setattr(Project, "edit_module_diagram", project_edit_diagram)
    runner = CliRunner()
    read_result = runner.invoke(
        build_cli_app(),
        [
            "module-diagram",
            str(project.root),
            "mio",
            "--profile",
            "hoi4",
            "--json",
        ],
    )
    edit_result = runner.invoke(
        build_cli_app(),
        [
            "module-diagram-edit",
            str(project.root),
            "focus_tree",
            "--request-json",
            dumps_json(
                {
                    "position_intents": [{"focus_id": "A"}],
                    "edge_intents": [{"kind": "prerequisite"}],
                }
            ),
            "--write",
            "--plan-hash",
            "reviewed-plan",
            "--json",
        ],
    )
    node_intents = [
        {
            "organization_id": "ORG",
            "parent_trait_id": "ROOT",
            "trait_id": "CHILD",
            "title": "Child",
            "x": 2,
            "y": 1,
            "source_revision": "sha256:" + ("a" * 64),
        }
    ]
    node_edit_result = runner.invoke(
        build_cli_app(),
        [
            "module-diagram-edit",
            str(project.root),
            "mio",
            "--request-json",
            dumps_json({"node_intents": node_intents}),
            "--json",
        ],
    )

    assert read_result.exit_code == 0, read_result.output
    assert edit_result.exit_code == 0, edit_result.output
    assert node_edit_result.exit_code == 0, node_edit_result.output
    assert loads_json(read_result.output)["family"] == "mio"
    assert loads_json(edit_result.output)["status"] == "applied"
    help_result = runner.invoke(
        build_cli_app(),
        ["module-diagram", "--help"],
    )
    assert help_result.exit_code == 0, help_result.output
    assert "registered" in help_result.output.lower()

    toolkit = create_authoring_mcp_toolkit()
    schema_by_name = {row["function"]["name"]: row["function"]["parameters"] for row in toolkit.to_openai_tools()}
    assert schema_by_name["module_diagram"]["required"] == ["path", "family"]
    assert schema_by_name["module_diagram"]["properties"]["family"]["pattern"] == "^[a-z][a-z0-9_-]*$"
    edit_schema = schema_by_name["module_diagram_edit"]
    assert edit_schema["required"] == ["path", "family"]
    assert edit_schema["properties"]["family"]["pattern"] == "^[a-z][a-z0-9_-]*$"
    assert edit_schema["properties"]["position_intents"]["maxItems"] == (MAX_MODULE_DIAGRAM_POSITION_INTENTS)
    assert edit_schema["properties"]["edge_intents"]["maxItems"] == (MAX_MODULE_DIAGRAM_EDGE_INTENTS)
    assert edit_schema["properties"]["node_intents"]["maxItems"] == (MAX_MODULE_DIAGRAM_NODE_INTENTS)
    assert edit_schema["properties"]["position_intents"]["items"]["type"] == "object"
    assert edit_schema["properties"]["edge_intents"]["items"]["type"] == "object"
    toolkit.run(
        "module_diagram",
        path=str(project.root),
        family="military_industrial_organization",
    )
    toolkit.run(
        "module_diagram_edit",
        path=str(project.root),
        family="mio",
        node_intents=node_intents,
    )

    assert calls == [
        ("read", {"family": "mio", "profile": "hoi4"}),
        (
            "edit",
            {
                "family": "focus_tree",
                "profile": None,
                "position_intents": [{"focus_id": "A"}],
                "edge_intents": [{"kind": "prerequisite"}],
                "node_intents": [],
                "write": True,
                "plan_hash": "reviewed-plan",
            },
        ),
        (
            "edit",
            {
                "family": "mio",
                "profile": None,
                "position_intents": [],
                "edge_intents": [],
                "node_intents": node_intents,
                "write": False,
                "plan_hash": None,
            },
        ),
        (
            "read",
            {
                "family": "military_industrial_organization",
                "profile": None,
            },
        ),
        (
            "edit",
            {
                "family": "mio",
                "profile": None,
                "position_intents": [],
                "edge_intents": [],
                "node_intents": [
                    {
                        "organization_id": "ORG",
                        "parent_trait_id": "ROOT",
                        "trait_id": "CHILD",
                        "title": "Child",
                        "x": 2,
                        "y": 1,
                        "source_revision": "sha256:" + ("a" * 64),
                    }
                ],
                "write": False,
                "plan_hash": None,
            },
        ),
    ]


def test_module_diagram_contract_tables_link_every_python_surface() -> None:
    project_rows = {row["symbol"]: row for row in get_project_api_table()["rows"]}
    cli_rows = {row["symbol"]: row for row in get_cli_api_table()["rows"]}
    rest_rows = {row["symbol"]: row for row in get_rest_api_table()["rows"]}
    mcp_rows = {row["symbol"]: row for row in get_mcp_api_table()["rows"]}

    assert project_rows["Project.module_diagram"]["frontend_operation_ids"] == ["module.diagram"]
    assert project_rows["Project.edit_module_diagram"]["frontend_operation_ids"] == ["module.diagram.edit"]
    assert cli_rows["paradev module-diagram"]["adapter"] == ("Project.module_diagram")
    assert cli_rows["paradev module-diagram-edit"]["adapter"] == ("Project.edit_module_diagram")
    assert rest_rows[f"GET {MODULE_DIAGRAM_PATH}"]["frontend_operation_ids"] == ["module.diagram"]
    assert rest_rows[f"POST {MODULE_DIAGRAM_EDIT_PATH}"]["frontend_operation_ids"] == ["module.diagram.edit"]
    assert mcp_rows["module_diagram"]["mode"] == "read"
    assert mcp_rows["module_diagram_edit"]["mode"] == "write"
