"""Registry-backed collection authoring contracts."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from shutil import copytree

import pytest

from paradev.sdk.project import Project, create_project
from paradev.sdk.templates import (
    COLLECTION_SCAFFOLD_SCHEMA,
    ProjectTemplateSpecError,
    project_module_templates,
)

_PIHC3_FOCUS_EXTENSION = Path(__file__).resolve().parents[1] / "projects" / "PIHC3" / "extensions" / "focus"


@pytest.mark.unit
def test_project_template_kind_is_explicit_and_validated(
    tmp_path: Path,
) -> None:
    manifest_path = tmp_path / "paradev.yaml"
    collection = project_module_templates(
        {
            "example:tree/basic": {
                "kind": "collection",
                "family": "focus",
                "files": {"def.txt": "focus_tree = {{ id = {object_id} }}\n"},
            }
        },
        manifest_path,
    )[0]
    module = project_module_templates(
        {
            "example:focus/basic": {
                "family": "focus",
                "files": {"def.txt": "focus = {{ id = {object_id} }}\n"},
            }
        },
        manifest_path,
    )[0]

    assert collection.kind == "collection"
    assert collection.to_view()["kind"] == "collection"
    assert module.kind == "module"
    assert module.to_view()["kind"] == "module"

    with pytest.raises(ProjectTemplateSpecError, match="collection, module"):
        project_module_templates(
            {
                "example:invalid": {
                    "kind": "tree",
                    "family": "focus",
                    "files": {"def.txt": "invalid = yes\n"},
                }
            },
            manifest_path,
        )


@pytest.mark.unit
def test_project_template_advanced_flag_must_be_boolean(
    tmp_path: Path,
) -> None:
    with pytest.raises(ProjectTemplateSpecError, match="advanced must be a boolean"):
        project_module_templates(
            {
                "example:invalid": {
                    "family": "focus",
                    "args": {"source": {"advanced": "yes"}},
                    "files": {"def.txt": "{source}"},
                }
            },
            tmp_path / "paradev.yaml",
        )


@pytest.mark.integration
def test_pihc3_focus_tree_template_creates_node_and_compiles_partials(
    tmp_path: Path,
) -> None:
    root = tmp_path / "PIHC3"
    create_project(root, project_id="PIHC3", title="PIHC3 Focus Smoke")
    copytree(
        _PIHC3_FOCUS_EXTENSION,
        root / "extensions" / "focus",
    )
    project = Project.load(root)
    tree_values = {
        "title": "测试国策树",
        "country_tag": "C01",
    }

    templates = project.templates(family="focus")["templates"]
    assert {(row["id"], row["kind"], row["authoring_ready"]) for row in templates} == {
        ("pihc3:focus/basic", "module", True),
        ("pihc3:focus-tree/basic", "collection", True),
    }

    dry = project.scaffold_collection(
        "focus",
        "C01_CODEX",
        values=tree_values,
    )
    assert dry["schema"] == COLLECTION_SCAFFOLD_SCHEMA
    assert dry["blocked"] is False
    assert dry["written"] is False
    assert dry["folder_name"] == "C01_CODEX - 测试国策树"
    assert dry["files"][0]["collection_path"] == "def.txt"
    assert dry["authoring_plan"]["authoring_path"]["collection_id"] == "C01_CODEX"

    missing_hash = project.scaffold_collection(
        "focus",
        "C01_CODEX",
        values=tree_values,
        write=True,
    )
    assert missing_hash["blocked"] is True
    assert missing_hash["written"] is False
    assert missing_hash["diagnostics"][-1]["code"] == ("collection_scaffold.plan_hash_required")

    applied = project.scaffold_collection(
        "focus",
        "C01_CODEX",
        values=tree_values,
        write=True,
        plan_hash=str(dry["plan_hash"]),
    )
    assert applied["blocked"] is False
    assert applied["written"] is True
    assert applied["applied"] is True
    tree_path = root / "src" / "collections" / "focus" / "C01_CODEX - 测试国策树" / "def.txt"
    assert "id = C01_CODEX" in tree_path.read_text(encoding="utf-8")
    assert "tag = C01" in tree_path.read_text(encoding="utf-8")

    discovered = project.discover_collections(
        family="focus",
        collection_id="C01_CODEX",
    )
    assert [row.collection_id for row in discovered.collections] == ["C01_CODEX"]
    diagram = project.module_diagram("focus_tree")
    tree = diagram["trees"][0]
    node_intent = {
        "tree_id": "C01_CODEX",
        "focus_id": "C01_CODEX_START",
        "x": 0,
        "y": 0,
        "title": "起点",
        "description": "测试国策",
    }
    node_dry = project.edit_module_diagram("focus_tree", node_intents=[node_intent])
    assert node_dry["intent"]["tree_source_revision"] == tree["source_revision"]
    node_apply = project.edit_module_diagram(
        "focus_tree",
        node_intents=[node_intent],
        write=True,
        plan_hash=str(node_dry["plan_hash"]),
    )
    assert node_apply["written"] is True

    module_build = project.build(
        family="focus",
        module_id="focus/C01_CODEX_START",
    )
    collection_build = project.build(
        family="focus",
        collection_id="C01_CODEX",
    )
    assert not [row for row in module_build.diagnostics if row.severity == "error"]
    assert not [row for row in collection_build.diagnostics if row.severity == "error"]
    assert len(module_build.artifacts) == 4
    assert len(collection_build.artifacts) == 4
    assert project.module_diagram("focus_tree")["summary"]["node_count"] == 1


@pytest.mark.pihc3
@pytest.mark.integration
def test_collection_scaffold_creates_a_missing_source_root_on_first_use(
    tmp_path: Path,
) -> None:
    root = tmp_path / "PIHC3"
    create_project(root, project_id="PIHC3", title="PIHC3 First-use Smoke")
    copytree(
        _PIHC3_FOCUS_EXTENSION,
        root / "extensions" / "focus",
    )
    source_root = root / "not-created-yet"
    project = replace(
        Project.load(root),
        source_roots=(source_root,),
    )
    values = {"title": "首个国策树", "country_tag": "C01"}

    reviewed = project.scaffold_collection(
        "focus",
        "C01_FIRST_USE",
        values=values,
    )
    applied = project.scaffold_collection(
        "focus",
        "C01_FIRST_USE",
        values=values,
        write=True,
        plan_hash=str(reviewed["plan_hash"]),
    )

    assert source_root.exists()
    assert reviewed["blocked"] is False
    assert reviewed["written"] is False
    assert applied["blocked"] is False
    assert applied["written"] is True
    assert applied["applied"] is True
    assert (source_root / "collections" / "focus" / "C01_FIRST_USE - 首个国策树" / "def.txt").is_file()


@pytest.mark.pihc3
@pytest.mark.integration
def test_collection_scaffold_rejects_stale_reviewed_plan(
    tmp_path: Path,
) -> None:
    root = tmp_path / "PIHC3"
    create_project(root, project_id="PIHC3", title="PIHC3 Focus Smoke")
    copytree(
        _PIHC3_FOCUS_EXTENSION,
        root / "extensions" / "focus",
    )
    project = Project.load(root)
    reviewed_values = {"title": "旧标题", "country_tag": "C01"}
    reviewed = project.scaffold_collection(
        "focus",
        "C01_STALE",
        values=reviewed_values,
    )

    current = project.scaffold_collection(
        "focus",
        "C01_STALE",
        values={"title": "新标题", "country_tag": "C01"},
        write=True,
        plan_hash=str(reviewed["plan_hash"]),
    )

    assert current["blocked"] is True
    assert current["written"] is False
    assert current["diagnostics"][-1]["code"] == ("collection_scaffold.plan_hash_mismatch")
    assert not (root / "src" / "collections" / "focus" / "C01_STALE - 新标题").exists()
