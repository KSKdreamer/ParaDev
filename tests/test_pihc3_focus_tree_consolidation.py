from __future__ import annotations

from pathlib import Path

import pytest
from heavenbase.utils import copy_dir, load_yaml, save_txt, save_yaml

from paradev.build import BuildResult, Diagnostic
from paradev.sdk import Project

pytestmark = pytest.mark.integration

PIHC3_ROOT = Path("projects/PIHC3").resolve()
FOCUS_ROOT = PIHC3_ROOT / "src/modules/focus"
COLLECTION_ROOT = PIHC3_ROOT / "src/collections/focus"


def _mapping(path: Path) -> dict[str, object]:
    value = load_yaml(str(path), strict=True)
    assert isinstance(value, dict)
    return value


def _write_focus_authoring_project(tmp_path: Path) -> Project:
    project_root = tmp_path / "PIHC3"
    copy_dir(PIHC3_ROOT / "extensions/focus", project_root / "extensions/focus")
    save_yaml(
        {
            "project_id": "PIHC3",
            "title": "PIHC3 Focus Test",
            "game": "hoi4",
            "source_roots": ["src"],
            "output_root": "build/mod",
            "build_root": ".paradev/cache/build",
        },
        str(project_root / "paradev.yaml"),
    )
    collection = project_root / "src/collections/focus/TEST_TREE - 测试树"
    collection.mkdir(parents=True)
    save_txt(
        "focus_tree = {\n  id = TEST_TREE\n  default = no\n}\n",
        str(collection / "def.txt"),
    )
    module = project_root / "src/modules/focus/FOCUS_TEST_START - 开始"
    module.mkdir(parents=True)
    save_yaml(
        {"collection": "TEST_TREE"},
        str(module / ".paradev/meta.yaml"),
    )
    save_txt(
        "focus = {\n  id = FOCUS_TEST_START\n  x = 0\n  y = 0\n}\n",
        str(module / "def.txt"),
    )
    save_txt(
        "[en.FOCUS_TEST_START]\nStart\n\n" "[en.FOCUS_TEST_START_desc]\nStart description\n",
        str(module / "main.loc"),
    )
    return Project.load(project_root)


def test_pihc3_focus_entity_replaces_aggregate_family_through_registry() -> None:
    project = Project.load(PIHC3_ROOT)
    registry = project._build_registry(profile=project.game)
    family = registry.family("focus")
    slots = {slot.name: slot for slot in registry.source_slots_for("focus")}
    collection_slots = {slot.name: slot for slot in registry.collection_source_slots_for("focus")}

    assert family.__class__.__name__ == "PIHC3FocusFamily"
    assert family.member_container == "focus_tree"
    assert family.aggregate_member_localization is True
    assert family.copy_path_template == "{source_path}"
    assert registry.publication_replacements_for("focus") == ()
    assert not hasattr(family, "retired_families")
    assert slots["def"].required is True
    assert slots["preview"].match == "preview.png"
    assert slots["compiled_assets"].kind == "copy"
    assert collection_slots["def"].required is True
    with pytest.raises(ValueError, match="not registered"):
        registry.family("focus_tree")


def test_pihc3_focus_modules_and_collections_are_minimal_and_self_contained() -> None:
    modules = sorted(path for path in FOCUS_ROOT.iterdir() if path.is_dir())
    collections = sorted(path for path in COLLECTION_ROOT.iterdir() if path.is_dir())

    assert len(modules) == 738
    assert len(collections) == 28
    assert not (PIHC3_ROOT / "src/modules/focus_tree").exists()
    assert not (PIHC3_ROOT / "src/modules/focus_asset_component").exists()
    assert all(" - " in path.name for path in (*modules, *collections))
    assert len(list(FOCUS_ROOT.glob("*/preview.png"))) == 738
    assert len(list(FOCUS_ROOT.glob("*/gfx/interface/goals/*.dds"))) == 738
    assert len(list(FOCUS_ROOT.glob("*/interface/focuses/*.gfx"))) == 738
    assert len(list(COLLECTION_ROOT.glob("*/gfx/interface/goals/*.dds"))) == 1
    assert not list(FOCUS_ROOT.glob("*/legacy"))
    assert not list(COLLECTION_ROOT.glob("*/legacy"))
    assert not list(COLLECTION_ROOT.glob("*/.paradev/meta.yaml"))

    for module in modules:
        assert not (module / "meta.yaml").exists()
        assert set(_mapping(module / ".paradev/meta.yaml")) == {"collection"}
        assert (module / "def.txt").read_text(encoding="utf-8").count("focus =") >= 1
    for collection in collections:
        assert not (collection / "meta.yaml").exists()
        assert "focus_tree = {" in (collection / "def.txt").read_text(encoding="utf-8")


def test_pihc3_focus_collection_diagram_maps_nodes_to_owned_sources() -> None:
    diagram = Project.load(PIHC3_ROOT).module_diagram("focus")
    nodes = {node["id"]: node for node in diagram["nodes"]}
    edges = {(edge["kind"], edge["source"], edge["target"]) for edge in diagram["edges"]}

    assert diagram["source_kind"] == "focus_collection_modules"
    assert len(diagram["trees"]) == 28
    assert len(nodes) == 738
    assert diagram["diagnostics"] == []
    assert diagram["editable"] is True
    canterlot = nodes["FOCUS_C08_CANTERLOT_PACT"]
    assert canterlot["tree_id"] == "C08_MAIN"
    assert canterlot["module_id"] == "focus/FOCUS_C08_CANTERLOT_PACT"
    assert canterlot["collection_id"] == "C08_MAIN"
    assert canterlot["source_path"].startswith("src/modules/focus/")
    assert canterlot["source_path"].endswith("/def.txt")
    assert canterlot["image_path"].endswith("/preview.png")
    assert (PIHC3_ROOT / canterlot["source_path"]).is_file()
    assert (PIHC3_ROOT / canterlot["image_path"]).is_file()
    assert (
        "prerequisite",
        "FOCUS_C08_SPARKING_FIRE",
        "FOCUS_C08_CONTACT_COMRADES",
    ) in edges


def test_pihc3_focus_collection_partial_build_preserves_output_contract() -> None:
    result = Project.load(PIHC3_ROOT).build(family="focus")
    paths = {str(artifact.path) for artifact in result.artifacts}

    assert result.blocked is False
    assert len(result.modules) == 738
    assert len(result.collections) == 28
    assert len(result.diagnostics) == 0
    assert "common/national_focus/C08_MAIN.txt" in paths
    assert "localisation/english/FOCUS_TREE_C08_MAIN_l_english.yml" in paths
    assert "interface/focuses/FOCUS_C08_CANTERLOT_PACT.gfx" in paths
    assert "gfx/interface/goals/FOCUS_C08_CANTERLOT_PACT.dds" in paths


def test_focus_collection_editor_creates_standalone_module(
    tmp_path: Path,
) -> None:
    project = _write_focus_authoring_project(tmp_path)
    project_root = project.root
    projection = project.module_diagram("focus")
    tree = projection["trees"][0]
    request = {
        "tree_id": "TEST_TREE",
        "focus_id": "FOCUS_TEST_NEXT",
        "x": 1,
        "y": 1,
        "title": "Next",
        "description": "Next description",
        "prerequisite_id": "FOCUS_TEST_START",
    }

    plan = project.edit_module_diagram("focus", node_intents=[request])
    applied = project.edit_module_diagram(
        "focus",
        node_intents=[request],
        write=True,
        plan_hash=plan["plan_hash"],
    )

    assert tree["source_revision"] == plan["intent"]["tree_source_revision"]
    assert plan["provider_schema"] == "paradev.pihc3.focus-node-module-create.v1"
    assert plan["blocked"] is False
    assert applied["blocked"] is False
    assert applied["written"] is True
    created = project_root / "src/modules/focus/FOCUS_TEST_NEXT - Next"
    assert not (created / "meta.yaml").exists()
    assert _mapping(created / ".paradev/meta.yaml") == {"collection": "TEST_TREE"}
    assert "prerequisite = {" in (created / "def.txt").read_text(encoding="utf-8")
    result = project.build(family="focus", emit_artifacts=True)
    assert result.blocked is False
    output = project_root / "build/mod/common/national_focus/TEST_TREE.txt"
    output_text = output.read_text(encoding="utf-8")
    assert output_text.count("id = FOCUS_TEST_START") == 1
    assert output_text.count("id = FOCUS_TEST_NEXT") == 1
    node = next(row for row in project.module_diagram("focus")["nodes"] if row["id"] == "FOCUS_TEST_NEXT")
    edit = project.edit_module_diagram(
        "focus",
        position_intents=[
            {
                "focus_id": "FOCUS_TEST_NEXT",
                "x": 2,
                "y": 1,
                "source_revision": node["source_revision"],
            }
        ],
    )
    edited = project.edit_module_diagram(
        "focus",
        position_intents=[
            {
                "focus_id": "FOCUS_TEST_NEXT",
                "x": 2,
                "y": 1,
                "source_revision": node["source_revision"],
            }
        ],
        write=True,
        plan_hash=edit["plan_hash"],
    )
    assert edited["blocked"] is False
    assert edited["written"] is True
    assert "x = 2" in (created / "def.txt").read_text(encoding="utf-8")


def test_focus_collection_editor_rolls_back_new_module_on_build_rejection(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _write_focus_authoring_project(tmp_path)
    request = {
        "tree_id": "TEST_TREE",
        "focus_id": "FOCUS_TEST_REJECTED",
        "x": 1,
        "y": 1,
        "title": "Rejected",
        "description": "This module must not survive build rejection.",
    }
    plan = project.edit_module_diagram("focus", node_intents=[request])

    def rejected_build(
        _project: Project,
        **_options: object,
    ) -> BuildResult:
        return BuildResult.plan(
            "focus",
            profile="hoi4",
            diagnostics=(
                Diagnostic(
                    code="test.focus_build_rejected",
                    message="Synthetic project-local Focus build rejection.",
                ),
            ),
        )

    monkeypatch.setattr(Project, "build", rejected_build)
    rejected = project.edit_module_diagram(
        "focus",
        node_intents=[request],
        write=True,
        plan_hash=plan["plan_hash"],
    )

    assert rejected["blocked"] is True
    assert rejected["written"] is False
    assert any(row["code"] == "module_diagram.build_rejected" for row in rejected["diagnostics"])
    assert not (project.root / "src/modules/focus/FOCUS_TEST_REJECTED - Rejected").exists()


def test_focus_collection_editor_rejects_stale_tree_context(
    tmp_path: Path,
) -> None:
    project = _write_focus_authoring_project(tmp_path)
    request = {
        "tree_id": "TEST_TREE",
        "focus_id": "FOCUS_TEST_STALE",
        "x": 1,
        "y": 1,
        "title": "Stale",
        "description": "The reviewed tree changes before apply.",
    }
    plan = project.edit_module_diagram("focus", node_intents=[request])
    tree_path = project.root / "src/collections/focus/TEST_TREE - 测试树/def.txt"
    tree_path.write_text(
        f"{tree_path.read_text(encoding='utf-8')}# concurrent tree edit\n",
        encoding="utf-8",
    )

    stale = project.edit_module_diagram(
        "focus",
        node_intents=[request],
        write=True,
        plan_hash=plan["plan_hash"],
    )

    assert stale["blocked"] is True
    assert stale["written"] is False
    assert any(row["code"] == "module_diagram.plan_hash_mismatch" for row in stale["diagnostics"])
    assert not (project.root / "src/modules/focus/FOCUS_TEST_STALE - Stale").exists()
