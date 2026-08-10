from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

import pytest
from heavenbase.utils import copy_dir, save_txt, save_yaml

from paradev.build import BuildResult, Diagnostic
from paradev.sdk import Project

os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
sys.dont_write_bytecode = True
pytestmark = pytest.mark.integration

PIHC3_ROOT = Path(os.environ.get("PARADEV_PIHC3_ROOT", "projects/PIHC3")).expanduser().resolve()
TECHNOLOGY_ROOT = PIHC3_ROOT / "src/modules/technology"
SUPPORT_MODULE_ROOT = TECHNOLOGY_ROOT / "PIHC_TECHNOLOGY_SUPPORT - 共享技术支持"
SUPPORT_PATHS = (
    Path("common/technologies/electronic_mechanical_engineering.txt"),
    Path("common/technologies/industry.txt"),
)


def _module_roots(root: Path) -> list[Path]:
    return [path for path in sorted(root.iterdir(), key=lambda candidate: candidate.name) if path.is_dir() and not path.name.startswith(".")]


def _object_id(module_root: Path) -> str:
    return module_root.name.split(" - ", 1)[0]


def _materialize_minimal_support_project(root: Path) -> Path:
    technology_root = root / "src/modules/technology"
    technology_root.mkdir(parents=True)
    shutil.copytree(
        SUPPORT_MODULE_ROOT,
        technology_root / SUPPORT_MODULE_ROOT.name,
    )
    shutil.copytree(
        PIHC3_ROOT / "extensions/technology",
        root / "extensions/technology",
    )
    (root / "paradev.yaml").write_text(
        """project_id: PIHC3
title: Minimal PIHC3 technology support
game: hoi4
source_roots: [src]
output_root: build/mod
build_root: .paradev/.cache/build
""",
        encoding="utf-8",
    )
    return root


def _write_technology_authoring_project(tmp_path: Path) -> Project:
    project_root = tmp_path / "PIHC3"
    copy_dir(
        PIHC3_ROOT / "extensions/technology",
        project_root / "extensions/technology",
    )
    save_yaml(
        {
            "project_id": "PIHC3",
            "title": "PIHC3 Technology Test",
            "game": "hoi4",
            "preferred_language": "zh",
            "source_roots": ["src"],
            "output_root": "build/mod",
            "build_root": ".paradev/cache/build",
        },
        str(project_root / "paradev.yaml"),
    )
    parent = project_root / "src/modules/technology/TECH_TEST_PARENT - 前置科技"
    parent.mkdir(parents=True)
    save_txt(
        "technologies = {\n"
        "\tTECH_TEST_PARENT = {\n"
        "\t\tfolder = {\n"
        "\t\t\tname = infantry_folder\n"
        "\t\t\tposition = { x = 0 y = 0 }\n"
        "\t\t}\n"
        "\t\tcategories = { pihc_all }\n"
        "\t\tresearch_cost = 1\n"
        "\t\tstart_year = 1936\n"
        "\t}\n"
        "}\n",
        str(parent / "def.txt"),
    )
    save_txt(
        "[zh.TECH_TEST_PARENT]\n前置科技\n\n" "[zh.TECH_TEST_PARENT_desc]\n前置科技说明\n",
        str(parent / "main.loc"),
    )
    support = project_root / "src/modules/technology/PIHC_TECHNOLOGY_SUPPORT - 共享技术支持"
    shared = support / "common/technologies/pihc_test_shared.txt"
    shared.parent.mkdir(parents=True)
    save_txt("technologies = {\n}\n", str(shared))
    return Project.load(project_root)


def test_pihc3_technology_family_owns_nodes_assets_and_shared_sources() -> None:
    project = Project.load(PIHC3_ROOT)
    registry = project._build_registry(profile=project.game)
    technology = registry.family("technology")
    technology_slots = {slot.name: slot for slot in registry.source_slots_for("technology")}
    assert tuple(technology_slots) == (
        "def",
        "loc",
        "preview",
        "compiled_assets",
        "shared_pdx",
    )
    assert technology_slots["def"].kind == "pdx"
    assert technology_slots["def"].required is False
    assert technology_slots["loc"].kind == "loc"
    assert technology_slots["loc"].many is True
    assert technology_slots["preview"].match == "icon.png"
    assert technology_slots["preview"].regex is False
    assert technology_slots["compiled_assets"].kind == "copy"
    assert technology_slots["compiled_assets"].many is True
    assert technology_slots["shared_pdx"].kind == "pdx"
    assert technology_slots["shared_pdx"].many is True
    assert technology.pdx_path_template == "common/technologies/{object_id}.txt"
    assert technology.copy_path_template == "{source_path}"
    assert registry.publication_replacements_for("technology") == ()
    assert not hasattr(technology, "retired_families")

    with pytest.raises(ValueError, match="is not registered"):
        registry.family("technology_support")
    with pytest.raises(ValueError, match="is not registered"):
        registry.family("technology_asset_component")
    with pytest.raises(ValueError, match="is not registered"):
        registry.family("technology_component")


def test_pihc3_technology_without_icon_exposes_one_exact_optional_png_target() -> None:
    object_id = "TECHNOLOGY_CANNON_HEAVY_CONTEMPORARY"
    project = Project.load(PIHC3_ROOT)
    [item] = project.browser(
        kind="module",
        module_id=f"technology/{object_id}",
    )["items"]
    module_root = PIHC3_ROOT / "src/modules/technology" / f"{object_id} - 重型现代加农炮"
    icon = module_root / "icon.png"

    assert item["image_targets"] == [
        {
            "slot": "preview",
            "slot_kinds": [],
            "name": "icon.png",
            "path": str(icon),
            "relative_path": icon.relative_to(PIHC3_ROOT).as_posix(),
            "extension": "png",
            "exists": False,
        }
    ]


def test_pihc3_technology_modules_are_minimal_portable_single_sources_of_truth() -> None:
    all_modules = _module_roots(TECHNOLOGY_ROOT)
    technology_modules = [module_root for module_root in all_modules if module_root != SUPPORT_MODULE_ROOT]
    technology_ids: set[str] = set()

    assert len(technology_modules) == 300
    assert len(all_modules) == 301
    for module_root in technology_modules:
        object_id = _object_id(module_root)
        _object_id_part, folder_title = module_root.name.split(" - ", 1)

        assert object_id not in technology_ids
        technology_ids.add(object_id)
        assert folder_title
        assert not (module_root / "meta.yaml").exists()
        assert not (module_root / ".paradev").exists()
        assert (module_root / "def.txt").is_file()
        assert (module_root / "main.loc").is_file()
        assert not (module_root / "legacy").exists()
        assert not (module_root / "preview.png").exists()

    support_root = SUPPORT_MODULE_ROOT
    assert support_root.name == "PIHC_TECHNOLOGY_SUPPORT - 共享技术支持"
    assert not (support_root / "meta.yaml").exists()
    assert not (support_root / ".paradev").exists()
    assert len(technology_ids) == 300

    modules_root = PIHC3_ROOT / "src/modules"
    assert not (modules_root / "technology_asset_component").exists()
    assert not (modules_root / "technology_component").exists()
    assert not (modules_root / "technology_support").exists()
    assert not any(path.name == "legacy" for path in TECHNOLOGY_ROOT.rglob("*"))


@pytest.mark.parametrize(
    "missing_path",
    SUPPORT_PATHS,
    ids=("electronic-mechanical-engineering", "industry"),
)
def test_pihc3_technology_shared_sources_are_independently_editable(
    tmp_path: Path,
    missing_path: Path,
) -> None:
    project_root = _materialize_minimal_support_project(tmp_path / "minimal-pihc3")
    technology_root = project_root / "src/modules/technology"
    module_roots = _module_roots(technology_root)
    assert len(module_roots) == 1
    (module_roots[0] / missing_path).unlink()

    result = Project.load(project_root).build(
        family="technology",
        strict_metadata=True,
    )

    assert result.blocked is False
    assert not result.diagnostics
    assert missing_path.as_posix() not in {str(artifact.path) for artifact in result.artifacts}


@pytest.mark.parametrize(
    "malformed_relative_path",
    SUPPORT_PATHS,
    ids=("electronic-mechanical-engineering", "industry"),
)
def test_pihc3_technology_shared_source_rejects_malformed_pdx(
    tmp_path: Path,
    malformed_relative_path: Path,
) -> None:
    project_root = _materialize_minimal_support_project(tmp_path / "minimal-pihc3")
    support_modules = _module_roots(project_root / "src/modules/technology")
    assert len(support_modules) == 1
    malformed_path = support_modules[0] / malformed_relative_path
    malformed_path.write_text(
        "technologies = { malformed = {\n",
        encoding="utf-8",
    )

    result = Project.load(project_root).build(
        family="technology",
        strict_metadata=True,
    )

    assert result.blocked is True
    assert [diagnostic.code for diagnostic in result.diagnostics] == ["pdx.unclosed_block"]
    assert result.diagnostics[0].source_path == malformed_relative_path.as_posix()


def test_pihc3_technology_diagram_uses_authored_modules_and_skips_shared_support() -> None:
    project = Project.load(PIHC3_ROOT)
    diagram = project.module_diagram("technology")
    nodes = {str(row["id"]): row for row in diagram["nodes"]}
    technology = next(row for row in project.browser_summary()["families"] if row["family"] == "technology")

    assert diagram["source_kind"] == "pihc3_technology_modules"
    assert len(nodes) == 300
    assert diagram["summary"]["module_count"] == 301
    assert diagram["summary"]["support_module_count"] == 1
    assert diagram["support_module_ids"] == ["technology/PIHC_TECHNOLOGY_SUPPORT"]
    assert diagram["editable"] is True
    heavy_cannon = nodes["TECHNOLOGY_CANNON_HEAVY_CONTEMPORARY"]
    assert heavy_cannon["module_id"] == "technology/TECHNOLOGY_CANNON_HEAVY_CONTEMPORARY"
    assert heavy_cannon["localized_titles"]["l_simp_chinese"] == "重型现代加农炮"
    assert heavy_cannon["source_path"].endswith("/def.txt")
    assert technology["diagram"]["authoring_kind"] == "diagram-node"
    assert technology["diagram"]["node_authoring"]["requires_selection"] is False
    assert technology["diagram"]["node_authoring"]["selection_defaults"] == [
        {"field": "folder", "source": "folder"},
        {"field": "prerequisite_id", "source": "id"},
        {"field": "x", "source": "x"},
        {"field": "y", "source": "y", "offset": 2},
    ]
    assert "selection_defaults" not in technology["diagram"]


def test_pihc3_technology_diagram_creates_standalone_module(
    tmp_path: Path,
) -> None:
    project = _write_technology_authoring_project(tmp_path)
    request = {
        "technology_id": "TECH_TEST_CHILD",
        "title": "后续科技",
        "description": "后续科技说明",
        "folder": "infantry_folder",
        "category": "pihc_all",
        "research_cost": 1.25,
        "start_year": 1938,
        "x": 1,
        "y": 2,
        "prerequisite_id": "TECH_TEST_PARENT",
    }

    plan = project.edit_module_diagram("technology", node_intents=[request])
    created = project.root / "src/modules/technology/TECH_TEST_CHILD - 后续科技"
    assert plan["provider_schema"] == "paradev.pihc3.technology-node-module-create.v1"
    assert plan["blocked"] is False
    assert plan["intent"]["language"] == "zh"
    assert plan["intent"]["folder_sources"] == [
        {
            "technology_id": "TECH_TEST_PARENT",
            "source_path": "src/modules/technology/TECH_TEST_PARENT - 前置科技/def.txt",
            "source_revision": plan["intent"]["prerequisite_source_revision"],
        }
    ]
    assert not created.exists()

    applied = project.edit_module_diagram(
        "technology",
        node_intents=[request],
        write=True,
        plan_hash=plan["plan_hash"],
    )

    assert applied["blocked"] is False
    assert applied["written"] is True
    assert created.is_dir()
    assert not (created / "meta.yaml").exists()
    assert not (created / ".paradev").exists()
    assert "TECH_TEST_PARENT = 1" in (created / "def.txt").read_text(encoding="utf-8")
    assert "[zh.TECH_TEST_CHILD]" in (created / "main.loc").read_text(encoding="utf-8")
    build = project.build(family="technology")
    assert build.blocked is False
    diagram = project.module_diagram("technology")
    assert any(row["id"] == "TECH_TEST_CHILD" for row in diagram["nodes"])
    assert any(row["kind"] == "dependency" and row["source"] == "TECH_TEST_PARENT" and row["target"] == "TECH_TEST_CHILD" for row in diagram["edges"])
    with pytest.raises(ValueError, match="already exists"):
        project.edit_module_diagram("technology", node_intents=[request])


def test_pihc3_technology_diagram_rolls_back_new_module_on_build_rejection(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _write_technology_authoring_project(tmp_path)
    request = {
        "technology_id": "TECH_TEST_REJECTED",
        "title": "拒绝科技",
    }
    plan = project.edit_module_diagram("technology", node_intents=[request])

    def rejected_build(
        _project: Project,
        **_options: object,
    ) -> BuildResult:
        return BuildResult.plan(
            "technology",
            profile="hoi4",
            diagnostics=(
                Diagnostic(
                    code="test.technology_build_rejected",
                    message="Synthetic project-local Technology build rejection.",
                ),
            ),
        )

    monkeypatch.setattr(Project, "build", rejected_build)
    rejected = project.edit_module_diagram(
        "technology",
        node_intents=[request],
        write=True,
        plan_hash=plan["plan_hash"],
    )

    assert rejected["blocked"] is True
    assert rejected["written"] is False
    assert any(row["code"] == "module_diagram.build_rejected" for row in rejected["diagnostics"])
    assert not (project.root / "src/modules/technology/TECH_TEST_REJECTED - 拒绝科技").exists()


def test_pihc3_technology_diagram_rejects_stale_folder_context(
    tmp_path: Path,
) -> None:
    project = _write_technology_authoring_project(tmp_path)
    request = {
        "technology_id": "TECH_TEST_STALE",
        "title": "过期科技",
        "folder": "infantry_folder",
        "category": "pihc_all",
    }
    plan = project.edit_module_diagram("technology", node_intents=[request])
    parent = project.root / "src/modules/technology/TECH_TEST_PARENT - 前置科技/def.txt"
    parent.write_text(
        f"{parent.read_text(encoding='utf-8')}# concurrent tree edit\n",
        encoding="utf-8",
    )

    stale = project.edit_module_diagram(
        "technology",
        node_intents=[request],
        write=True,
        plan_hash=plan["plan_hash"],
    )

    assert stale["blocked"] is True
    assert stale["written"] is False
    assert any(row["code"] == "module_diagram.plan_hash_mismatch" for row in stale["diagnostics"])
    assert not (project.root / "src/modules/technology/TECH_TEST_STALE - 过期科技").exists()
