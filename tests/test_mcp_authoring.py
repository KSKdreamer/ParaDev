import asyncio
import base64
import os
import sys
from pathlib import Path

import pytest
from fastmcp import Client
from fastmcp.client.transports import StdioTransport
from heavenbase.utils import copy_dir
from typer.testing import CliRunner

from paradev.cli import build_app
from paradev.hb import _paradev_context
from paradev.sdk import Project
from paradev.sdk.project import MAX_MODULE_CREATE_BATCH_SIZE
from paradev.surfaces import mcp as mcp_surface
from paradev.surfaces.mcp import (
    create_authoring_mcp_server,
    create_authoring_mcp_toolkit,
    serve_authoring_mcp_stdio,
)

AUTHORING_TOOL_NAMES = [
    "project_templates",
    "project_authoring_path",
    "project_authoring_plan",
    "project_browser",
    "module_file",
    "collection_file",
    "module_asset",
    "module_source_form",
    "module_source_form_update",
    "module_source_form_update_batch",
    "localization_workspace",
    "localization_plan",
    "project_create_modules",
    "project_preferred_language",
    "project_draft_apply",
    "collection_scaffold",
    "collection_remove",
    "module_duplicate",
    "module_collection_set",
    "module_activity_set",
    "module_metadata_clean",
    "module_diagram",
    "module_diagram_edit",
]
PIHC3_IDEA_EXTENSION = Path(__file__).resolve().parents[1] / "projects" / "PIHC3" / "extensions" / "idea"


def test_authoring_mcp_toolkit_plans_and_applies_module_batch(tmp_path: Path) -> None:
    project = Project.create(tmp_path / "starter", title="Starter")
    modules = [
        {
            "family": "idea",
            "object_id": object_id,
            "values": {"title": f"Idea {object_id}"},
        }
        for object_id in ("A", "B")
    ]
    toolkit = create_authoring_mcp_toolkit()
    context = _paradev_context()

    assert toolkit.name == "paradev-authoring"
    assert list(toolkit.tools) == AUTHORING_TOOL_NAMES
    assert toolkit._resolver is context.modules()
    assert toolkit._config is context.config
    for tool in toolkit.tools.values():
        assert tool.capsule._resolver is context.modules()
        assert tool.capsule._config is context.config
        serializer = tool._serializer_capsule()
        assert serializer._resolver is context.modules()
        assert serializer._config is context.config
    schema_by_name = {row["function"]["name"]: row["function"]["parameters"] for row in toolkit.to_openai_tools()}
    assert schema_by_name["project_templates"]["required"] == ["path"]
    assert schema_by_name["project_authoring_path"]["properties"]["kind"]["enum"] == [
        "module",
        "collection",
    ]
    assert schema_by_name["project_authoring_plan"]["required"] == [
        "path",
        "kind",
        "family",
        "target_id",
    ]
    browser_schema = schema_by_name["project_browser"]
    assert browser_schema["required"] == ["path"]
    assert browser_schema["properties"]["kind"]["anyOf"][0]["enum"] == [
        "module",
        "collection",
    ]
    module_file_schema = schema_by_name["module_file"]
    assert module_file_schema["required"] == [
        "path",
        "module_id",
        "relative_path",
    ]
    assert module_file_schema["properties"]["encoding"] == {
        "type": "string",
        "enum": ["utf-8"],
        "default": "utf-8",
    }
    collection_file_schema = schema_by_name["collection_file"]
    assert collection_file_schema["required"] == [
        "path",
        "collection_id",
        "relative_path",
    ]
    assert collection_file_schema["properties"]["family"] == {
        "anyOf": [
            {"type": "string", "minLength": 1},
            {"type": "null"},
        ],
        "default": None,
        "description": "Optional collection family used to disambiguate the id.",
    }
    module_asset_schema = schema_by_name["module_asset"]
    assert module_asset_schema["required"] == [
        "path",
        "module_id",
        "relative_path",
    ]
    assert module_asset_schema["additionalProperties"] is False
    assert module_asset_schema["properties"]["include_content"] == {
        "type": "boolean",
        "default": False,
        "description": ("Include bounded base64 content. Keep false when only the " "digest and draft guard are needed."),
    }
    source_form_schema = schema_by_name["module_source_form"]
    assert source_form_schema["required"] == [
        "path",
        "module_id",
        "relative_path",
    ]
    assert source_form_schema["properties"]["relative_path"] == {
        "type": "string",
        "minLength": 1,
        "description": ("Canonical Registry-owned JSON or PDX source path relative " "to the module folder."),
    }
    source_form_update_schema = schema_by_name["module_source_form_update"]
    assert source_form_update_schema["required"] == [
        "path",
        "module_id",
        "relative_path",
        "values",
    ]
    assert source_form_update_schema["properties"]["values"]["minProperties"] == 1
    source_form_update_batch_schema = schema_by_name["module_source_form_update_batch"]
    assert source_form_update_batch_schema["required"] == ["path", "updates"]
    batch_updates_schema = source_form_update_batch_schema["properties"]["updates"]
    assert batch_updates_schema["minItems"] == 1
    assert batch_updates_schema["maxItems"] == 256
    assert batch_updates_schema["items"]["required"] == [
        "module_id",
        "relative_path",
        "values",
    ]
    assert batch_updates_schema["items"]["properties"]["values"]["minProperties"] == 1
    localization_workspace_schema = schema_by_name["localization_workspace"]
    assert localization_workspace_schema["required"] == [
        "path",
        "target_kind",
        "target_id",
    ]
    localization_plan_schema = schema_by_name["localization_plan"]
    assert localization_plan_schema["required"] == [
        "path",
        "target_kind",
        "target_id",
        "operation",
    ]
    assert [row["properties"]["op"]["const"] for row in localization_plan_schema["properties"]["operation"]["oneOf"]] == ["set", "add", "rename", "remove"]
    schema = schema_by_name["project_create_modules"]
    assert schema["required"] == ["path", "modules"]
    assert schema["properties"]["modules"]["type"] == "array"
    assert schema["properties"]["write"] == {"type": "boolean", "default": False}
    assert "force" not in schema["properties"]
    language_schema = schema_by_name["project_preferred_language"]
    assert language_schema["required"] == ["path", "preferred_language"]
    assert language_schema["properties"]["preferred_language"]["enum"] == [
        "en",
        "fr",
        "de",
        "ru",
        "es",
        "pl",
        "pt_br",
        "zh",
        "ja",
        "ko",
    ]
    assert language_schema["allOf"][0]["then"]["required"] == ["plan_hash"]
    draft_schema = schema_by_name["project_draft_apply"]
    assert draft_schema["required"] == ["path"]
    assert draft_schema["additionalProperties"] is False
    assert draft_schema["properties"]["module_rename"]["required"] == [
        "module_id",
        "object_id",
    ]
    assert draft_schema["anyOf"][-1] == {"required": ["module_rename"]}
    collection_schema = schema_by_name["collection_scaffold"]
    assert collection_schema["required"] == [
        "path",
        "template_id",
        "collection_id",
    ]
    assert collection_schema["properties"]["values"] == {
        "type": "object",
        "additionalProperties": True,
        "default": {},
    }
    assert collection_schema["properties"]["write"] == {
        "type": "boolean",
        "default": False,
    }
    assert collection_schema["properties"]["force"] == {
        "type": "boolean",
        "default": False,
    }
    assert collection_schema["allOf"][0]["then"]["required"] == ["plan_hash"]
    collection_remove_schema = schema_by_name["collection_remove"]
    assert collection_remove_schema["required"] == ["path", "collection_id"]
    assert collection_remove_schema["properties"]["write"] == {
        "type": "boolean",
        "default": False,
    }
    assert collection_remove_schema["allOf"][0]["then"]["required"] == ["plan_hash"]
    duplicate_schema = schema_by_name["module_duplicate"]
    assert duplicate_schema["required"] == ["path", "module_id", "object_id"]
    assert duplicate_schema["properties"]["write"] == {
        "type": "boolean",
        "default": False,
    }
    assert duplicate_schema["properties"]["plan_hash"]["default"] is None
    collection_membership_schema = schema_by_name["module_collection_set"]
    assert collection_membership_schema["required"] == ["path", "module_id"]
    assert collection_membership_schema["properties"]["collection_id"] == {
        "anyOf": [
            {"type": "string", "minLength": 1},
            {"type": "null"},
        ],
        "default": None,
        "description": "Target same-family collection id, or null to clear membership.",
    }
    assert collection_membership_schema["properties"]["write"] == {
        "type": "boolean",
        "default": False,
    }
    assert collection_membership_schema["allOf"][0]["then"]["required"] == ["plan_hash"]
    cleanup_schema = schema_by_name["module_metadata_clean"]
    assert cleanup_schema["required"] == ["path"]
    assert cleanup_schema["properties"]["write"] == {
        "type": "boolean",
        "default": False,
    }
    assert cleanup_schema["properties"]["plan_hash"]["default"] is None
    assert cleanup_schema["allOf"][0]["then"]["required"] == ["plan_hash"]
    assert type(toolkit.to_fastmcp()).__name__ == "FastMCP"

    templates = toolkit.run(
        "project_templates",
        path=str(project.root),
        family="idea",
        authoring_ready=True,
    )
    assert templates["schema"] == "paradev.sdk.templates.v1"
    assert [template["family"] for template in templates["templates"]] == ["idea"]

    authoring_plan = toolkit.run(
        "project_authoring_plan",
        path=str(project.root),
        kind="module",
        family="idea",
        target_id="A",
    )
    assert authoring_plan["schema"] == "paradev.sdk.authoring_plan.v1"
    assert authoring_plan["authoring_path"]["exists"] is False

    plan = toolkit.run(
        "project_create_modules",
        path=str(project.root),
        modules=modules,
    )

    assert plan["schema"] == "paradev.sdk.module_batch.v1"
    assert plan["blocked"] is False
    assert plan["applied"] is False
    assert plan["counts"]["create"] == 2

    applied = toolkit.run(
        "project_create_modules",
        path=str(project.root),
        modules=modules,
        write=True,
        plan_hash=plan["plan_hash"],
    )

    assert applied["blocked"] is False
    assert applied["applied"] is True
    assert applied["counts"]["created"] == 2
    assert (project.root / "src/modules/idea/B/meta.yaml").is_file()

    language_plan = toolkit.run(
        "project_preferred_language",
        path=str(project.root),
        preferred_language="zh",
    )
    language_applied = toolkit.run(
        "project_preferred_language",
        path=str(project.root),
        preferred_language="zh",
        write=True,
        plan_hash=language_plan["plan_hash"],
    )

    assert language_plan["written"] is False
    assert language_applied["written"] is True
    assert Project.load(project.root).preferred_language == "zh"

    asset_path = project.root / "src/modules/idea/B/icon.png"
    asset_path.write_bytes(b"\x89PNG\r\n\x1a\nasset")
    browser = toolkit.run(
        "project_browser",
        path=str(project.root),
        kind="module",
        module_id="idea/B",
    )
    source = toolkit.run(
        "module_file",
        path=str(project.root),
        module_id="idea/B",
        relative_path="def.txt",
    )
    asset = toolkit.run(
        "module_asset",
        path=str(project.root),
        module_id="idea/B",
        relative_path="icon.png",
    )
    asset_content = toolkit.run(
        "module_asset",
        path=str(project.root),
        module_id="idea/B",
        relative_path="icon.png",
        include_content=True,
    )
    source_form = toolkit.run(
        "module_source_form",
        path=str(project.root),
        module_id="idea/B",
        relative_path="def.txt",
    )

    assert [row["module_id"] for row in browser["items"]] == ["idea/B"]
    assert source["module_id"] == "idea/B"
    assert source["size"] == len(source["text"].encode("utf-8"))
    assert source["mtime_ns"].isdigit()
    assert asset["schema"] == "paradev.module.asset.v1"
    assert asset["source_slots"] == [{"name": "icon", "kinds": ["copy"]}]
    assert asset["content_included"] is False
    assert "content_base64" not in asset
    assert asset["draft_guard"] == {
        "path": "src/modules/idea/B/icon.png",
        "expected_size": asset["size"],
        "expected_mtime_ns": asset["mtime_ns"],
    }
    assert base64.b64decode(asset_content["content_base64"], validate=True) == (asset_path.read_bytes())
    assert source_form["schema"] == "paradev.mcp.module-source-form.v1"
    assert source_form["module_id"] == "idea/B"
    assert source_form["supported"] is True
    assert source_form["source"]["text"] == source["text"]
    assert source_form["source"]["size"] == source["size"]
    assert source_form["source"]["mtime_ns"].isdigit()
    assert source_form["form"]["source_format"] == "pdx"


def test_authoring_mcp_collection_remove_forwards_guarded_plan(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = Project.create(tmp_path / "starter", title="Starter")
    calls: list[dict[str, object]] = []

    def remove_collection(
        self: Project,
        collection_id: str,
        *,
        family: str | None = None,
        source_root: str | None = None,
        write: bool = False,
        plan_hash: str | None = None,
    ) -> dict[str, object]:
        calls.append(
            {
                "collection_id": collection_id,
                "family": family,
                "source_root": source_root,
                "write": write,
                "plan_hash": plan_hash,
            }
        )
        return {
            "schema": "paradev.collection.remove.v1",
            "blocked": False,
            "removed": write,
            "plan_hash": "reviewed-plan",
        }

    monkeypatch.setattr(Project, "remove_collection", remove_collection)
    toolkit = create_authoring_mcp_toolkit()
    plan = toolkit.run(
        "collection_remove",
        path=str(project.root),
        collection_id="germany",
        family="event",
        source_root="src",
    )
    applied = toolkit.run(
        "collection_remove",
        path=str(project.root),
        collection_id="germany",
        family="event",
        write=True,
        plan_hash=plan["plan_hash"],
    )

    assert plan["removed"] is False
    assert applied["removed"] is True
    assert calls == [
        {
            "collection_id": "germany",
            "family": "event",
            "source_root": "src",
            "write": False,
            "plan_hash": None,
        },
        {
            "collection_id": "germany",
            "family": "event",
            "source_root": None,
            "write": True,
            "plan_hash": "reviewed-plan",
        },
    ]


@pytest.mark.integration
def test_authoring_mcp_creates_and_strictly_builds_five_pihc3_ideas(
    tmp_path: Path,
) -> None:
    project = Project.create(tmp_path / "PIHC3", title="PIHC3 MCP Idea Probe")
    copy_dir(
        PIHC3_IDEA_EXTENSION,
        project.root / "extensions" / "idea",
    )
    toolkit = create_authoring_mcp_toolkit()
    language_plan = toolkit.run(
        "project_preferred_language",
        path=str(project.root),
        preferred_language="zh",
    )
    toolkit.run(
        "project_preferred_language",
        path=str(project.root),
        preferred_language="zh",
        write=True,
        plan_hash=language_plan["plan_hash"],
    )
    catalog = toolkit.run(
        "project_templates",
        path=str(project.root),
        family="idea",
        authoring_ready=True,
    )
    modules = [
        {
            "template_id": "pihc3:idea/basic",
            "object_id": f"AGENT_IDEA_{name}",
            "values": {
                "title": name,
                "description": f"Agent-created idea {name}.",
                "cic": cic,
            },
        }
        for name, cic in zip(
            ("A", "B", "C", "D", "E"),
            (0.02, 0.05, 0.08, 0.12, 0.16),
            strict=True,
        )
    ]
    plan = toolkit.run(
        "project_create_modules",
        path=str(project.root),
        modules=modules,
    )
    applied = toolkit.run(
        "project_create_modules",
        path=str(project.root),
        modules=modules,
        write=True,
        plan_hash=plan["plan_hash"],
    )
    result = Project.load(project.root).build(
        family="idea",
        strict_metadata=True,
    )
    definitions = sorted((project.root / "src" / "modules" / "idea").glob("*/def.txt"))

    assert [row["id"] for row in catalog["templates"]] == ["pihc3:idea/basic"]
    assert catalog["templates"][0]["args"]["cic"]["description"] == ("Decimal factory-output modifier; use 0.02 for 2%.")
    assert plan["counts"] == {
        "create": 5,
        "created": 0,
        "unchanged": 0,
        "blocked": 0,
    }
    assert applied["counts"] == {
        "create": 0,
        "created": 5,
        "unchanged": 0,
        "blocked": 0,
    }
    assert not [diagnostic for diagnostic in result.diagnostics if diagnostic.severity == "error"]
    assert [path.parent.name for path in definitions] == [
        "AGENT_IDEA_A - A",
        "AGENT_IDEA_B - B",
        "AGENT_IDEA_C - C",
        "AGENT_IDEA_D - D",
        "AGENT_IDEA_E - E",
    ]
    assert [next(line.strip() for line in path.read_text(encoding="utf-8").splitlines() if "industrial_capacity_factory" in line) for path in definitions] == [
        "industrial_capacity_factory = 0.02",
        "industrial_capacity_factory = 0.05",
        "industrial_capacity_factory = 0.08",
        "industrial_capacity_factory = 0.12",
        "industrial_capacity_factory = 0.16",
    ]


def test_authoring_mcp_module_source_form_pairs_registry_projection_with_snapshot(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = Project.create(tmp_path / "starter", title="Starter")
    project.scaffold_module(
        "idea",
        "IDEA_GUIDED",
        values={"title": "Guided"},
        write=True,
    )
    expected_form = {
        "schema": "paradev.source-form.v1",
        "project_id": project.project_id,
        "family": "idea",
        "module_id": "idea/IDEA_GUIDED",
        "source_format": "pdx",
        "contract": "paradev.pdx.guided-form.v1",
        "sections": [],
    }
    calls: list[dict[str, object]] = []

    def source_form(
        self: Project,
        source_path: str,
        *,
        text: str | None = None,
        query: str | None = None,
    ) -> dict[str, object]:
        calls.append({"source_path": source_path, "text": text, "query": query})
        return expected_form

    monkeypatch.setattr(Project, "source_form", source_form)
    payload = create_authoring_mcp_toolkit().run(
        "module_source_form",
        path=str(project.root),
        module_id="idea/IDEA_GUIDED",
        relative_path="def.txt",
        query="IDEA_GUIDED",
    )

    source = payload["source"]
    assert payload["supported"] is True
    assert payload["form"] == expected_form
    assert source["module_id"] == "idea/IDEA_GUIDED"
    assert source["size"] == len(source["text"].encode("utf-8"))
    assert source["mtime_ns"].isdigit()
    assert calls == [{"source_path": source["path"], "text": source["text"], "query": "IDEA_GUIDED"}]


def test_authoring_mcp_guided_values_plan_one_guarded_source_edit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = Project.create(tmp_path / "starter", title="Starter")
    project.scaffold_module(
        "idea",
        "IDEA_GUIDED",
        values={"title": "Guided"},
        write=True,
    )
    expected = {
        "schema": "paradev.source-form-update.v1",
        "module_id": "idea/IDEA_GUIDED",
        "changed": True,
        "source_edit": {"path": "def.txt", "text": "updated"},
    }
    calls: list[dict[str, object]] = []

    def plan_source_form_update(
        self: Project,
        source_path: str,
        values: dict[str, object],
        *,
        query: str | None = None,
    ) -> dict[str, object]:
        calls.append({"source_path": source_path, "values": values, "query": query})
        return expected

    monkeypatch.setattr(Project, "plan_source_form_update", plan_source_form_update)
    payload = create_authoring_mcp_toolkit().run(
        "module_source_form_update",
        path=str(project.root),
        module_id="idea/IDEA_GUIDED",
        relative_path="def.txt",
        values={"pdx-control-000": "IDEA_GUIDED_UPDATED"},
        query="IDEA_GUIDED",
    )

    assert payload == expected
    assert calls == [
        {
            "source_path": str(project.root / "src/modules/idea/IDEA_GUIDED/def.txt"),
            "values": {"pdx-control-000": "IDEA_GUIDED_UPDATED"},
            "query": "IDEA_GUIDED",
        }
    ]


def test_authoring_mcp_guided_batch_resolves_sources_and_forwards_one_sdk_plan(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = Project.create(tmp_path / "starter", title="Starter")
    for object_id in ("IDEA_ALPHA", "IDEA_BETA"):
        project.scaffold_module(
            "idea",
            object_id,
            values={"title": object_id.title()},
            write=True,
        )
    expected = {
        "schema": "paradev.source-form-update-batch.v1",
        "project_id": project.project_id,
        "changed": True,
        "source_edits": [],
    }
    calls: list[list[dict[str, object]]] = []

    def plan_source_form_updates(
        self: Project,
        updates: list[dict[str, object]],
    ) -> dict[str, object]:
        calls.append(updates)
        return expected

    monkeypatch.setattr(
        Project,
        "plan_source_form_updates",
        plan_source_form_updates,
    )
    payload = create_authoring_mcp_toolkit().run(
        "module_source_form_update_batch",
        path=str(project.root),
        updates=[
            {
                "module_id": "idea/IDEA_ALPHA",
                "relative_path": "def.txt",
                "values": {"pdx-control-000": "IDEA_ALPHA_UPDATED"},
            },
            {
                "module_id": "idea/IDEA_BETA",
                "relative_path": "def.txt",
                "values": {"pdx-control-000": "IDEA_BETA_UPDATED"},
                "query": "IDEA_BETA",
            },
        ],
    )

    assert payload == expected
    assert calls == [
        [
            {
                "source_path": str(project.root / "src/modules/idea/IDEA_ALPHA/def.txt"),
                "values": {"pdx-control-000": "IDEA_ALPHA_UPDATED"},
            },
            {
                "source_path": str(project.root / "src/modules/idea/IDEA_BETA/def.txt"),
                "values": {"pdx-control-000": "IDEA_BETA_UPDATED"},
                "query": "IDEA_BETA",
            },
        ]
    ]


@pytest.mark.skipif(
    os.name != "posix",
    reason="Descriptor-anchored duplicate publication is POSIX-only.",
)
def test_authoring_mcp_toolkit_plans_and_applies_module_duplicate(
    tmp_path: Path,
) -> None:
    project = Project.create(tmp_path / "starter", title="Starter")
    toolkit = create_authoring_mcp_toolkit()

    plan = toolkit.run(
        "module_duplicate",
        path=str(project.root),
        module_id="modifier/starter_starter_modifier",
        object_id="starter_duplicate",
    )
    applied = toolkit.run(
        "module_duplicate",
        path=str(project.root),
        module_id="modifier/starter_starter_modifier",
        object_id="starter_duplicate",
        write=True,
        plan_hash=plan["plan_hash"],
    )

    assert plan["schema"] == "paradev.sdk.module_duplicate.v1"
    assert plan["status"] == "planned"
    assert applied["status"] == "duplicated"
    assert applied["identity_mode"] == "rewrite"
    assert applied["content_rewritten"] is True
    assert (project.root / "src/modules/modifier/starter_duplicate").is_dir()


def test_authoring_mcp_toolkit_forwards_guarded_metadata_cleanup(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = Project.create(tmp_path / "starter", title="Starter")
    calls: list[dict[str, object]] = []

    def cleanup(
        self: Project,
        *,
        family: str | None = None,
        module_id: str | None = None,
        source_root: str | None = None,
        write: bool = False,
        plan_hash: str | None = None,
    ) -> dict[str, object]:
        calls.append(
            {
                "family": family,
                "module_id": module_id,
                "source_root": source_root,
                "write": write,
                "plan_hash": plan_hash,
            }
        )
        return {
            "schema": "paradev.sdk.module_metadata_cleanup.v1",
            "applied": write,
            "blocked": False,
            "plan_hash": "reviewed-plan",
        }

    monkeypatch.setattr(Project, "clean_module_metadata", cleanup)
    toolkit = create_authoring_mcp_toolkit()
    plan = toolkit.run(
        "module_metadata_clean",
        path=str(project.root),
        family="idea",
        source_root="src",
    )
    applied = toolkit.run(
        "module_metadata_clean",
        path=str(project.root),
        module_id="idea/sample",
        write=True,
        plan_hash=plan["plan_hash"],
    )

    assert plan["applied"] is False
    assert applied["applied"] is True
    assert calls == [
        {
            "family": "idea",
            "module_id": None,
            "source_root": "src",
            "write": False,
            "plan_hash": None,
        },
        {
            "family": None,
            "module_id": "idea/sample",
            "source_root": None,
            "write": True,
            "plan_hash": "reviewed-plan",
        },
    ]


def test_authoring_mcp_toolkit_forwards_guarded_module_collection_update(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = Project.create(tmp_path / "starter", title="Starter")
    calls: list[dict[str, object]] = []

    def update_collection(
        self: Project,
        module_id: str,
        collection_id: str | None,
        *,
        source_root: str | None = None,
        write: bool = False,
        plan_hash: str | None = None,
    ) -> dict[str, object]:
        calls.append(
            {
                "module_id": module_id,
                "collection_id": collection_id,
                "source_root": source_root,
                "write": write,
                "plan_hash": plan_hash,
            }
        )
        return {
            "schema": "paradev.sdk.module_collection_update.v1",
            "applied": write,
            "blocked": False,
            "plan_hash": "reviewed-plan",
        }

    monkeypatch.setattr(Project, "set_module_collection", update_collection)
    toolkit = create_authoring_mcp_toolkit()
    plan = toolkit.run(
        "module_collection_set",
        path=str(project.root),
        module_id="modifier/starter_starter_modifier",
        collection_id="starter_modifiers",
        source_root="src",
    )
    applied = toolkit.run(
        "module_collection_set",
        path=str(project.root),
        module_id="modifier/starter_starter_modifier",
        collection_id=None,
        write=True,
        plan_hash=plan["plan_hash"],
    )

    assert plan["applied"] is False
    assert applied["applied"] is True
    assert calls == [
        {
            "module_id": "modifier/starter_starter_modifier",
            "collection_id": "starter_modifiers",
            "source_root": "src",
            "write": False,
            "plan_hash": None,
        },
        {
            "module_id": "modifier/starter_starter_modifier",
            "collection_id": None,
            "source_root": None,
            "write": True,
            "plan_hash": "reviewed-plan",
        },
    ]


def test_authoring_mcp_toolkit_forwards_guarded_module_activity_update(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = Project.create(tmp_path / "starter", title="Starter")
    calls: list[dict[str, object]] = []

    def update_activity(
        self: Project,
        module_id: str,
        active: bool,
        *,
        source_root: str | None = None,
        write: bool = False,
        plan_hash: str | None = None,
    ) -> dict[str, object]:
        calls.append(
            {
                "module_id": module_id,
                "active": active,
                "source_root": source_root,
                "write": write,
                "plan_hash": plan_hash,
            }
        )
        return {
            "schema": "paradev.sdk.module_activity_update.v1",
            "applied": write,
            "blocked": False,
            "plan_hash": "reviewed-plan",
        }

    monkeypatch.setattr(Project, "set_module_active", update_activity)
    toolkit = create_authoring_mcp_toolkit()
    plan = toolkit.run(
        "module_activity_set",
        path=str(project.root),
        module_id="modifier/starter_starter_modifier",
        active=False,
        source_root="src",
    )
    applied = toolkit.run(
        "module_activity_set",
        path=str(project.root),
        module_id="modifier/starter_starter_modifier",
        active=True,
        write=True,
        plan_hash=plan["plan_hash"],
    )

    assert plan["applied"] is False
    assert applied["applied"] is True
    assert calls == [
        {
            "module_id": "modifier/starter_starter_modifier",
            "active": False,
            "source_root": "src",
            "write": False,
            "plan_hash": None,
        },
        {
            "module_id": "modifier/starter_starter_modifier",
            "active": True,
            "source_root": None,
            "write": True,
            "plan_hash": "reviewed-plan",
        },
    ]


def test_authoring_mcp_fastmcp_preserves_schema_and_calls_tool(tmp_path: Path) -> None:
    project = Project.create(tmp_path / "starter", title="Starter")
    project.manifest_path.write_text(
        f"{project.manifest_path.read_text(encoding='utf-8')}preferred_language: zh\n",
        encoding="utf-8",
    )
    project = Project.load(project.root)
    modules = [{"family": "idea", "object_id": "FAST_MCP", "values": {"title": "Fast MCP"}}]
    server = create_authoring_mcp_server()

    async def plan_over_mcp() -> tuple[dict[str, object], dict[str, object]]:
        async with Client(server) as client:
            tools = await client.list_tools()
            templates_result = await client.call_tool(
                "project_templates",
                {
                    "path": str(project.root),
                    "family": "idea",
                    "authoring_ready": True,
                },
            )
            result = await client.call_tool(
                "project_create_modules",
                {
                    "path": str(project.root),
                    "modules": modules,
                },
            )
        assert [tool.name for tool in tools] == AUTHORING_TOOL_NAMES
        assert isinstance(templates_result.data, dict)
        templates = templates_result.data
        assert templates_result.structured_content == templates
        assert templates["schema"] == "paradev.sdk.templates.v1"
        assert templates["preferred_language"] == "zh"
        assert templates["templates"][0]["family"] == "idea"
        assert templates["templates"][0]["args"]["language"]["default"] == "zh"
        assert isinstance(result.data, dict)
        assert result.structured_content == result.data
        tools_by_name = {tool.name: tool for tool in tools}
        return tools_by_name["project_create_modules"].inputSchema, result.data

    schema, plan = asyncio.run(plan_over_mcp())
    module_schema = schema["properties"]["modules"]["items"]

    assert schema["required"] == ["path", "modules"]
    assert schema["additionalProperties"] is False
    assert schema["properties"]["modules"]["minItems"] == 1
    assert schema["properties"]["modules"]["maxItems"] == MAX_MODULE_CREATE_BATCH_SIZE
    assert module_schema["required"] == ["object_id"]
    assert module_schema["additionalProperties"] is False
    assert module_schema["properties"]["object_id"]["minLength"] == 1
    assert module_schema["oneOf"] == [
        {"required": ["family"]},
        {"required": ["template_id"]},
        {"required": ["family_or_template"]},
    ]
    assert set(module_schema["properties"]) == {
        "object_id",
        "family",
        "template_id",
        "family_or_template",
        "values",
    }
    assert plan["schema"] == "paradev.sdk.module_batch.v1"
    assert plan["counts"]["create"] == 1
    assert plan["modules"][0]["values"]["language"] == "zh"
    assert not (project.root / "src/modules/idea/FAST_MCP").exists()


def test_authoring_mcp_applies_source_and_module_rename_transaction(
    tmp_path: Path,
) -> None:
    project = Project.create(tmp_path / "starter", title="Starter")
    project.scaffold_module(
        "idea",
        "IDEA_ALPHA",
        values={"title": "Alpha"},
        write=True,
    )
    previous_root = project.root / "src/modules/idea/IDEA_ALPHA"
    localization = previous_root / "main.loc"
    toolkit = create_authoring_mcp_toolkit()
    snapshot = toolkit.run(
        "module_file",
        path=str(project.root),
        module_id="idea/IDEA_ALPHA",
        relative_path="main.loc",
    )

    payload = toolkit.run(
        "project_draft_apply",
        path=str(project.root),
        source_edits=[
            {
                "path": str(localization),
                "text": "[en.IDEA_ALPHA]\nReadable Alpha\n",
                "expected_size": snapshot["size"],
                "expected_mtime_ns": snapshot["mtime_ns"],
            }
        ],
        module_rename={
            "module_id": "idea/IDEA_ALPHA",
            "object_id": "IDEA_ALPHA",
            "title": "Readable Alpha",
        },
    )

    renamed_root = project.root / "src/modules/idea/IDEA_ALPHA - Readable Alpha"
    assert payload["module_rename"]["root"] == str(renamed_root)
    assert not previous_root.exists()
    assert (renamed_root / "main.loc").read_text(encoding="utf-8") == ("[en.IDEA_ALPHA]\nReadable Alpha\n")


def test_authoring_mcp_module_snapshot_blocks_stale_source_edit(
    tmp_path: Path,
) -> None:
    project = Project.create(tmp_path / "starter", title="Starter")
    project.scaffold_module(
        "idea",
        "IDEA_ALPHA",
        values={"title": "Alpha"},
        write=True,
    )
    source_path = project.root / "src/modules/idea/IDEA_ALPHA/def.txt"
    toolkit = create_authoring_mcp_toolkit()
    snapshot = toolkit.run(
        "module_file",
        path=str(project.root),
        module_id="idea/IDEA_ALPHA",
        relative_path="def.txt",
    )
    source_path.write_text("external edit\n", encoding="utf-8")

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

    assert source_path.read_text(encoding="utf-8") == "external edit\n"


def test_authoring_mcp_stdio_disables_banner_and_reserves_stdout(monkeypatch, capsys) -> None:
    calls: dict[str, object] = {}

    class FakeServer:
        def run(self, **kwargs: object) -> None:
            calls["run"] = kwargs

    class FakeToolkit:
        def to_fastmcp(self) -> FakeServer:
            calls["to_fastmcp"] = True
            return FakeServer()

    monkeypatch.setattr(mcp_surface, "create_authoring_mcp_server", lambda: FakeToolkit().to_fastmcp())

    serve_authoring_mcp_stdio()

    captured = capsys.readouterr()
    assert captured.out == ""
    assert calls == {
        "to_fastmcp": True,
        "run": {
            "transport": "stdio",
            "show_banner": False,
            "log_level": "WARNING",
        },
    }


def test_mcp_serve_cli_is_a_silent_thin_adapter(monkeypatch) -> None:
    calls: list[str] = []
    monkeypatch.setattr(mcp_surface, "serve_authoring_mcp_stdio", lambda: calls.append("serve"))

    result = CliRunner().invoke(build_app(), ["mcp", "serve"])

    assert result.exit_code == 0, result.output
    assert result.output == ""
    assert calls == ["serve"]


def test_mcp_serve_cli_negotiates_over_real_stdio(tmp_path: Path) -> None:
    repository = Path(__file__).resolve().parents[1]
    stderr_path = tmp_path / "mcp-stderr.log"
    child_environment = dict(os.environ)
    source_root = str(repository / "src")
    inherited_python_path = child_environment.get("PYTHONPATH")
    child_environment["PYTHONPATH"] = source_root if not inherited_python_path else source_root + os.pathsep + inherited_python_path
    transport = StdioTransport(
        command=sys.executable,
        args=[
            "-c",
            "from paradev.cli import main; raise SystemExit(main())",
            "mcp",
            "serve",
        ],
        env=child_environment,
        cwd=str(repository),
        keep_alive=False,
        log_file=stderr_path,
    )

    async def list_tools_over_stdio() -> list[tuple[str, dict[str, object]]]:
        async with Client(transport, timeout=60, init_timeout=60) as client:
            tools = await client.list_tools()
        return [(tool.name, tool.inputSchema) for tool in tools]

    tools = asyncio.run(list_tools_over_stdio())
    schema_by_name = dict(tools)

    assert [name for name, _schema in tools] == AUTHORING_TOOL_NAMES
    assert schema_by_name["project_templates"]["required"] == ["path"]
    assert schema_by_name["project_authoring_path"]["properties"]["kind"]["enum"] == ["module", "collection"]
    assert schema_by_name["project_authoring_plan"]["required"] == ["path", "kind", "family", "target_id"]
    assert schema_by_name["project_browser"]["required"] == ["path"]
    assert schema_by_name["module_file"]["required"] == ["path", "module_id", "relative_path"]
    assert schema_by_name["collection_file"]["required"] == [
        "path",
        "collection_id",
        "relative_path",
    ]
    assert schema_by_name["module_source_form"]["required"] == ["path", "module_id", "relative_path"]
    assert schema_by_name["module_source_form_update"]["required"] == [
        "path",
        "module_id",
        "relative_path",
        "values",
    ]
    assert schema_by_name["module_source_form_update_batch"]["required"] == ["path", "updates"]
    assert schema_by_name["project_create_modules"]["required"] == ["path", "modules"]
    assert schema_by_name["project_preferred_language"]["required"] == ["path", "preferred_language"]
    assert schema_by_name["project_draft_apply"]["required"] == ["path"]
    assert schema_by_name["project_draft_apply"]["anyOf"][-1] == {"required": ["module_rename"]}
    assert schema_by_name["collection_scaffold"]["required"] == [
        "path",
        "template_id",
        "collection_id",
    ]
    assert schema_by_name["module_duplicate"]["required"] == ["path", "module_id", "object_id"]
    assert "ParaDev authoring" not in stderr_path.read_text(encoding="utf-8")
