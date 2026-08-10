"""Public surface coverage for Registry-backed collection scaffolding."""

from __future__ import annotations

from pathlib import Path
from shutil import copytree

import pytest
from heavenbase.utils import loads_json
from typer.testing import CliRunner

from paradev.cli import build_app
from paradev.sdk import Project, plan_frontend_api_rest_request
from paradev.sdk.project import create_project
from paradev.surfaces.mcp import create_authoring_mcp_toolkit

_PIHC3_FOCUS_EXTENSION = Path(__file__).resolve().parents[1] / "projects" / "PIHC3" / "extensions" / "focus"
pytestmark = pytest.mark.pihc3


def _focus_project(tmp_path: Path) -> Project:
    root = tmp_path / "PIHC3"
    create_project(root, project_id="PIHC3", title="PIHC3 Focus Surface Smoke")
    copytree(_PIHC3_FOCUS_EXTENSION, root / "extensions" / "focus")
    return Project.load(root)


def test_collection_scaffold_cli_plans_and_applies_focus_tree(
    tmp_path: Path,
) -> None:
    project = _focus_project(tmp_path)
    runner = CliRunner()
    arguments = [
        "collection-scaffold",
        str(project.root),
        "pihc3:focus-tree/basic",
        "C01_CLI",
        "--value",
        "title=命令行国策树",
        "--value",
        "country_tag=C01",
        "--json",
    ]

    planned = runner.invoke(build_app(), arguments)

    assert planned.exit_code == 0, planned.output
    plan = loads_json(planned.output)
    assert plan["schema"] == "paradev.sdk.collection_scaffold.v1"
    assert plan["written"] is False
    assert plan["folder_name"] == "C01_CLI - 命令行国策树"

    applied = runner.invoke(
        build_app(),
        [
            *arguments[:-1],
            "--write",
            "--plan-hash",
            str(plan["plan_hash"]),
            "--json",
        ],
    )

    assert applied.exit_code == 0, applied.output
    payload = loads_json(applied.output)
    assert payload["written"] is True
    assert (project.root / "src" / "collections" / "focus" / "C01_CLI - 命令行国策树" / "def.txt").is_file()


def test_collection_scaffold_mcp_plans_and_applies_focus_tree(
    tmp_path: Path,
) -> None:
    project = _focus_project(tmp_path)
    toolkit = create_authoring_mcp_toolkit()
    request = {
        "path": str(project.root),
        "template_id": "pihc3:focus-tree/basic",
        "collection_id": "C01_MCP",
        "values": {"title": "代理国策树", "country_tag": "C01"},
    }

    plan = toolkit.run("collection_scaffold", **request)
    applied = toolkit.run(
        "collection_scaffold",
        **request,
        write=True,
        plan_hash=plan["plan_hash"],
    )

    assert plan["written"] is False
    assert applied["written"] is True
    source_path = project.root / "src" / "collections" / "focus" / "C01_MCP - 代理国策树" / "def.txt"
    assert source_path.is_file()

    snapshot = toolkit.run(
        "collection_file",
        path=str(project.root),
        collection_id="C01_MCP",
        family="focus",
        relative_path="def.txt",
    )

    assert snapshot["path"] == str(source_path)
    assert snapshot["collection_relative_path"] == "def.txt"
    assert snapshot["size"] == source_path.stat().st_size
    assert snapshot["mtime_ns"] == str(source_path.stat().st_mtime_ns)
    assert snapshot["text"] == source_path.read_text(encoding="utf-8")

    source_path.write_text("external collection edit\n", encoding="utf-8")
    with pytest.raises(ValueError, match="changed after the draft was opened"):
        toolkit.run(
            "project_draft_apply",
            path=str(project.root),
            source_edits=[
                {
                    "path": snapshot["relative_path"],
                    "text": "stale agent edit\n",
                    "expected_size": snapshot["size"],
                    "expected_mtime_ns": snapshot["mtime_ns"],
                }
            ],
        )
    assert source_path.read_text(encoding="utf-8") == "external collection edit\n"


def test_collection_scaffold_frontend_rest_plan_executes(
    tmp_path: Path,
) -> None:
    testclient = pytest.importorskip("fastapi.testclient")
    from paradev.surfaces.rest import build_app as build_rest_app

    project = _focus_project(tmp_path)
    values = {"title": "界面国策树", "country_tag": "C01"}
    request = plan_frontend_api_rest_request(
        "collection.scaffold",
        {
            "path": str(project.root),
            "template_id": "pihc3:focus-tree/basic",
            "collection_id": "C01_REST",
            "values": values,
        },
    )

    assert request["method"] == "POST"
    assert request["path"] == "/projects/collections/scaffold"
    assert request["query"] == {
        "path": str(project.root),
        "template_id": "pihc3:focus-tree/basic",
        "collection_id": "C01_REST",
        "write": False,
        "force": False,
    }
    assert request["body"] == {"values": values}

    client = testclient.TestClient(build_rest_app())
    planned_response = client.post(
        request["path"],
        params=request["query"],
        json=request["body"],
    )

    assert planned_response.status_code == 200, planned_response.text
    plan = planned_response.json()
    applied_response = client.post(
        request["path"],
        params={
            **request["query"],
            "write": True,
            "plan_hash": plan["plan_hash"],
        },
        json=request["body"],
    )

    assert applied_response.status_code == 200, applied_response.text
    assert applied_response.json()["written"] is True
    assert (project.root / "src" / "collections" / "focus" / "C01_REST - 界面国策树" / "def.txt").is_file()
