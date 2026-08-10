from __future__ import annotations

import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pytest
import yaml
from heavenbase.utils import copy_dir, save_txt, save_yaml

from paradev.build import BuildResult, Diagnostic
from paradev.pdx import PDXBlock, PDXScalar
from paradev.sdk import Project

pytestmark = pytest.mark.integration

PIHC3_ROOT = Path(os.environ.get("PARADEV_PIHC3_ROOT", "projects/PIHC3")).expanduser().resolve()
DOCTRINE_ROOT = PIHC3_ROOT / "src/modules/doctrine"
SUPPORT_ROOT = PIHC3_ROOT / "src/modules/doctrine" / "PIHC_DOCTRINE_SUPPORT - 教义共享支持"
EXPECTED_SUPPORT_PATHS = {
    "common/doctrines/folders/doctrine_folders.txt",
    "common/doctrines/grand_doctrines/sea_grand_doctrines.txt",
    "common/doctrines/subdoctrines/sea/navy_capital_subdoctrines.txt",
    "common/doctrines/subdoctrines/sea/navy_carrier_doctrines.txt",
    "common/doctrines/subdoctrines/sea/navy_screen_doctrines.txt",
    "common/doctrines/subdoctrines/sea/navy_submarine_doctrines.txt",
    "common/doctrines/tracks/PIHC_air_doctrine_tracks.txt",
    "common/doctrines/tracks/PIHC_land_doctrine_tracks.txt",
    "common/doctrines/tracks/sea_doctrine_tracks.txt",
}
EXPECTED_SUPPORT_LOCALIZATION_PATHS = {
    "localisation/english/PIHC_DOCTRINE_REWARDS_l_english.yml",
    "localisation/simp_chinese/PIHC_DOCTRINE_REWARDS_l_simp_chinese.yml",
}


def _module_roots() -> list[Path]:
    return sorted(path for path in DOCTRINE_ROOT.iterdir() if path.is_dir() and path != SUPPORT_ROOT)


def _object_id(module_root: Path) -> str:
    object_id, separator, title = module_root.name.partition(" - ")
    assert separator == " - "
    assert object_id
    assert title
    return object_id


def _definition(module_root: Path) -> PDXBlock:
    return PDXBlock.from_str((module_root / "def.txt").read_text(encoding="utf-8"))


def _definition_block(module_root: Path) -> PDXBlock:
    root = _definition(module_root)
    assert len(root.entries) == 1
    block = root.entries[0].val
    assert isinstance(block, PDXBlock)
    return block


def _scalar(block: PDXBlock, key: str) -> str | None:
    for entry in block.entries:
        if entry.key_str == key and isinstance(entry.val, PDXScalar):
            return str(entry.val.val)
    return None


def _expected_definition_path(module_root: Path) -> str:
    object_id = _object_id(module_root)
    block = _definition_block(module_root)
    if _scalar(block, "folder"):
        return f"common/doctrines/grand_doctrines/{object_id}.txt"
    assert _scalar(block, "track")
    xp_type = _scalar(block, "xp_type")
    directory = {"air": "air", "army": "land", "navy": "sea"}[str(xp_type)]
    return f"common/doctrines/subdoctrines/{directory}/{object_id}.txt"


def _write_doctrine_authoring_project(tmp_path: Path) -> Project:
    project_root = tmp_path / "PIHC3"
    copy_dir(
        PIHC3_ROOT / "extensions/doctrine",
        project_root / "extensions/doctrine",
    )
    save_yaml(
        {
            "project_id": "PIHC3",
            "title": "PIHC3 Doctrine Test",
            "game": "hoi4",
            "preferred_language": "zh",
            "source_roots": ["src"],
            "output_root": "build/mod",
            "build_root": ".paradev/cache/build",
        },
        str(project_root / "paradev.yaml"),
    )
    successor = project_root / "src/modules/doctrine/DOCTRINE_TEST_SUCCESSOR - 后续教义"
    successor.mkdir(parents=True)
    save_txt(
        "DOCTRINE_TEST_SUCCESSOR = {\n"
        "\ttrack = infantry\n"
        "\tname = DOCTRINE_TEST_SUCCESSOR\n"
        "\tdescription = DOCTRINE_TEST_SUCCESSOR_desc\n"
        "\ticon = GFX_doctrine_mobile_warfare_medium\n"
        "\txp_cost = 100\n"
        "\txp_type = army\n"
        "\tplanning_speed = 0.05\n"
        "}\n",
        str(successor / "def.txt"),
    )
    save_txt(
        "[zh.DOCTRINE_TEST_SUCCESSOR]\n后续教义\n\n" "[zh.DOCTRINE_TEST_SUCCESSOR_desc]\n后续教义说明\n",
        str(successor / "main.loc"),
    )
    save_yaml(
        {
            "schema": "paradev.hoi4.doctrine-diagram-state.v1",
            "position": {"x": 3, "y": 5},
            "paths": [],
            "mutually_exclusive": [],
        },
        str(successor / ".paradev/diagram.yaml"),
    )
    return Project.load(project_root)


def test_pihc3_doctrines_are_current_standalone_single_sources() -> None:
    module_roots = _module_roots()
    object_ids = {_object_id(module_root) for module_root in module_roots}
    shapes: Counter[str] = Counter()

    assert len(module_roots) == 51
    assert len([path for path in DOCTRINE_ROOT.iterdir() if path.is_dir()]) == 52
    assert len(object_ids) == 51
    for module_root in module_roots:
        block = _definition_block(module_root)
        folder = _scalar(block, "folder")
        track = _scalar(block, "track")
        if folder:
            shapes["grand"] += 1
        else:
            assert track
            assert _scalar(block, "xp_type") in {"air", "army"}
            shapes["subdoctrine"] += 1

        assert not (module_root / "meta.yaml").exists()
        assert not (module_root / ".paradev/meta.yaml").exists()
        assert not (module_root / "legacy").exists()
        assert (module_root / "main.loc").is_file()
        assert (module_root / "icon.png").is_file()
        state = yaml.safe_load((module_root / ".paradev/diagram.yaml").read_text(encoding="utf-8"))
        assert state["schema"] == "paradev.hoi4.doctrine-diagram-state.v1"
        assert set(state["paths"]) <= object_ids
        assert set(state["mutually_exclusive"]) <= object_ids

    assert shapes == {"grand": 8, "subdoctrine": 43}
    assert SUPPORT_ROOT.name == "PIHC_DOCTRINE_SUPPORT - 教义共享支持"
    assert not (SUPPORT_ROOT / "meta.yaml").exists()
    assert not (SUPPORT_ROOT / ".paradev").exists()
    assert not (SUPPORT_ROOT / "legacy").exists()
    assert {path.relative_to(SUPPORT_ROOT).as_posix() for path in SUPPORT_ROOT.rglob("*.txt")} == EXPECTED_SUPPORT_PATHS
    assert {path.relative_to(SUPPORT_ROOT).as_posix() for path in SUPPORT_ROOT.rglob("*.yml")} == EXPECTED_SUPPORT_LOCALIZATION_PATHS


def test_pihc3_doctrine_family_emits_every_module_definition() -> None:
    project = Project.load(PIHC3_ROOT)
    result = project.build(family="doctrine")
    pdx_artifacts = {str(artifact.path): artifact for artifact in result.artifacts if artifact.artifact_type == "pdx"}
    expected_paths = {_expected_definition_path(module_root) for module_root in _module_roots()}
    node_artifacts = {path: artifact for path, artifact in pdx_artifacts.items() if path in expected_paths}
    support_localization_artifacts = {
        str(artifact.path): artifact for artifact in result.artifacts if str(artifact.path) in EXPECTED_SUPPORT_LOCALIZATION_PATHS
    }

    assert result.blocked is False
    assert result.diagnostics == ()
    assert len(result.modules) == 52
    assert set(pdx_artifacts) == expected_paths | EXPECTED_SUPPORT_PATHS
    assert len(pdx_artifacts) == 60
    assert set(support_localization_artifacts) == EXPECTED_SUPPORT_LOCALIZATION_PATHS
    assert all(
        artifact.artifact_type == "pihc3_localisation"
        and artifact.owner == "module:doctrine/PIHC_DOCTRINE_SUPPORT"
        and artifact.metadata["module_ids"] == ["doctrine/PIHC_DOCTRINE_SUPPORT"]
        for artifact in support_localization_artifacts.values()
    )
    assert len(node_artifacts) == 51
    assert Counter(path.split("/")[2] for path in node_artifacts) == {
        "grand_doctrines": 8,
        "subdoctrines": 43,
    }
    assert not any("PIHC_air_grand_doctrines.txt" in path for path in node_artifacts)
    assert not any("PIHC_land_grand_doctrines.txt" in path for path in node_artifacts)
    armor = node_artifacts["common/doctrines/subdoctrines/land/DOCTRINE_ARMY_0_1_ARMOR_BLADE.txt"]
    assert isinstance(armor.payload, PDXBlock)
    assert "army_speed_factor = 0.1" in armor.payload.to_str()


def test_pihc3_doctrine_support_partial_keeps_all_owned_resources() -> None:
    project = Project.load(PIHC3_ROOT)
    result = project.build(
        family="doctrine",
        module_id="PIHC_DOCTRINE_SUPPORT",
    )
    owned_paths = {str(artifact.path) for artifact in result.artifacts if artifact.owner == "module:doctrine/PIHC_DOCTRINE_SUPPORT"}

    assert result.blocked is False
    assert result.diagnostics == ()
    assert len(result.modules) == 1
    assert owned_paths == (EXPECTED_SUPPORT_PATHS | EXPECTED_SUPPORT_LOCALIZATION_PATHS)


def test_pihc3_doctrine_diagram_has_only_compilable_nodes() -> None:
    project = Project.load(PIHC3_ROOT)
    diagram = project.module_diagram("doctrine")
    doctrine_family = next(row for row in project.browser_summary()["families"] if row["family"] == "doctrine")
    armor = next(row for row in diagram["nodes"] if row["id"] == "DOCTRINE_ARMY_0_1_ARMOR_BLADE")

    assert diagram["editable"] is True
    assert diagram["diagnostics"] == []
    assert len(diagram["nodes"]) == 51
    assert diagram["summary"]["module_count"] == 52
    assert diagram["summary"]["support_module_count"] == 1
    assert diagram["support_module_ids"] == ["doctrine/PIHC_DOCTRINE_SUPPORT"]
    assert len(diagram["edges"]) == 79
    assert sum(edge["kind"] == "path" for edge in diagram["edges"]) == 54
    assert sum(edge["kind"] == "mutually_exclusive" for edge in diagram["edges"]) == 25
    assert all(node["editable"] is True for node in diagram["nodes"])
    assert armor["track"] == "infantry"
    assert armor["xp_type"] == "army"
    assert armor["localized_titles"]["l_simp_chinese"] == "步坦协同"
    assert armor["image_path"].endswith("/icon.png")
    assert doctrine_family["diagram"]["authoring_kind"] == "diagram-node"
    assert doctrine_family["diagram"]["node_authoring"]["requires_selection"] is False
    assert doctrine_family["diagram"]["node_authoring"]["selection_defaults"] == [
        {"field": "parent_doctrine_id", "source": "id"},
        {"field": "xp_type", "source": "xp_type"},
        {"field": "x", "source": "x"},
        {"field": "y", "source": "y", "offset": 2},
    ]
    assert "selection_defaults" not in doctrine_family["diagram"]


def test_pihc3_doctrine_diagram_creates_standalone_child_module(
    tmp_path: Path,
) -> None:
    project = _write_doctrine_authoring_project(tmp_path)
    request = {
        "doctrine_id": "DOCTRINE_TEST_NEW",
        "title": "新教义",
        "description": "新教义说明",
        "track": "infantry",
        "xp_type": "army",
        "x": 3,
        "y": 3,
        "parent_doctrine_id": "DOCTRINE_TEST_SUCCESSOR",
    }

    plan = project.edit_module_diagram("doctrine", node_intents=[request])
    created = project.root / "src/modules/doctrine/DOCTRINE_TEST_NEW - 新教义"

    assert plan["provider_schema"] == "paradev.pihc3.doctrine-node-module-create.v1"
    assert plan["blocked"] is False
    assert plan["intent"]["language"] == "zh"
    assert plan["intent"]["parent_source_revision"].startswith("sha256:")
    assert plan["source_plan"]["status"] == "planned"
    assert plan["source_replacements"] == [
        {
            "path": ("src/modules/doctrine/DOCTRINE_TEST_SUCCESSOR - 后续教义/" ".paradev/diagram.yaml"),
            "fields": ["paths"],
        }
    ]
    assert not created.exists()

    applied = project.edit_module_diagram(
        "doctrine",
        node_intents=[request],
        write=True,
        plan_hash=plan["plan_hash"],
    )

    assert applied["blocked"] is False
    assert applied["written"] is True
    assert created.is_dir()
    assert not (project.root / ".paradev/diagram-module-transaction/recovery.json").exists()
    assert not (created / "meta.yaml").exists()
    assert not (created / ".paradev/meta.yaml").exists()
    assert {path.relative_to(created).as_posix() for path in created.rglob("*") if path.is_file()} == {".paradev/diagram.yaml", "def.txt", "main.loc"}
    child_state = yaml.safe_load((created / ".paradev/diagram.yaml").read_text(encoding="utf-8"))
    assert child_state["paths"] == []
    parent_state = yaml.safe_load(
        (project.root / "src/modules/doctrine/DOCTRINE_TEST_SUCCESSOR - 后续教义/" ".paradev/diagram.yaml").read_text(encoding="utf-8")
    )
    assert parent_state["paths"] == ["DOCTRINE_TEST_NEW"]
    definition = (created / "def.txt").read_text(encoding="utf-8")
    assert "track = infantry" in definition
    assert "xp_type = army" in definition
    assert "[zh.DOCTRINE_TEST_NEW]" in (created / "main.loc").read_text(encoding="utf-8")
    build = project.build(family="doctrine")
    assert build.blocked is False
    assert {str(artifact.path) for artifact in build.artifacts if artifact.artifact_type == "pdx"} >= {
        "common/doctrines/subdoctrines/land/DOCTRINE_TEST_NEW.txt",
    }
    diagram = project.module_diagram("doctrine")
    assert any(row["id"] == "DOCTRINE_TEST_NEW" for row in diagram["nodes"])
    assert any(row["kind"] == "path" and row["source"] == "DOCTRINE_TEST_SUCCESSOR" and row["target"] == "DOCTRINE_TEST_NEW" for row in diagram["edges"])
    [item] = project.browser(
        kind="module",
        module_id="doctrine/DOCTRINE_TEST_NEW",
    )["items"]
    assert item["image_targets"] == [
        {
            "slot": "preview",
            "slot_kinds": [],
            "name": "icon.png",
            "path": str(created / "icon.png"),
            "relative_path": ("src/modules/doctrine/DOCTRINE_TEST_NEW - 新教义/icon.png"),
            "extension": "png",
            "exists": False,
        }
    ]


@pytest.mark.parametrize(
    ("crash_mode", "expected_child"),
    (
        ("before_parent", False),
        ("after_parent", True),
        ("before_parent_tampered", None),
    ),
)
def test_pihc3_doctrine_child_creation_recovers_hard_process_exit(
    tmp_path: Path,
    crash_mode: str,
    expected_child: bool | None,
) -> None:
    project = _write_doctrine_authoring_project(tmp_path)
    request = {
        "doctrine_id": f"DOCTRINE_CRASH_{crash_mode.upper()}",
        "title": f"崩溃恢复 {crash_mode}",
        "description": "硬退出恢复测试",
        "track": "infantry",
        "xp_type": "army",
        "x": 4,
        "y": 4,
        "parent_doctrine_id": "DOCTRINE_TEST_SUCCESSOR",
    }
    script = """
import os
from pathlib import Path
from paradev.sdk import Project
import paradev.sdk.project as project_module

root = Path(os.environ["PARADEV_CRASH_PROJECT"])
mode = os.environ["PARADEV_CRASH_MODE"]
project = Project.load(root)
request = __import__("json").loads(os.environ["PARADEV_CRASH_REQUEST"])
plan = project.edit_module_diagram("doctrine", node_intents=[request])
if mode.startswith("before_parent"):
    def crash_source(*args, **kwargs):
        os._exit(91)
    project_module._apply_source_draft_mutations = crash_source
else:
    recover = project_module._recover_diagram_module_transaction
    def crash_after_parent(current):
        marker = current.root / ".paradev/diagram-module-transaction/recovery.json"
        if marker.exists():
            os._exit(92)
        return recover(current)
    project_module._recover_diagram_module_transaction = crash_after_parent
project.edit_module_diagram(
    "doctrine",
    node_intents=[request],
    write=True,
    plan_hash=plan["plan_hash"],
)
raise SystemExit(99)
"""
    environment = {
        **os.environ,
        "PARADEV_CRASH_PROJECT": str(project.root),
        "PARADEV_CRASH_MODE": crash_mode,
        "PARADEV_CRASH_REQUEST": json.dumps(request, ensure_ascii=False),
    }

    crashed = subprocess.run(
        [sys.executable, "-c", script],
        check=False,
        cwd=Path(__file__).parents[1],
        env=environment,
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert crashed.returncode == (91 if crash_mode.startswith("before_parent") else 92)
    marker = project.root / ".paradev/diagram-module-transaction/recovery.json"
    child = project.root / "src/modules/doctrine" / f"{request['doctrine_id']} - {request['title']}"
    assert marker.is_file()
    assert child.is_dir()
    if expected_child is None:
        definition = child / "def.txt"
        definition.write_text(
            definition.read_text(encoding="utf-8") + "# external edit\n",
            encoding="utf-8",
        )

        with pytest.raises(ValueError, match="preserved recovery data"):
            project.build(family="doctrine")

        assert marker.is_file()
        assert definition.read_text(encoding="utf-8").endswith("# external edit\n")
        return

    recovered = project.build(family="doctrine")

    assert recovered.blocked is False
    assert child.exists() is expected_child
    assert not marker.exists()
    parent_state = yaml.safe_load(
        (project.root / "src/modules/doctrine/DOCTRINE_TEST_SUCCESSOR - 后续教义/" ".paradev/diagram.yaml").read_text(encoding="utf-8")
    )
    expected_paths = [request["doctrine_id"]] if expected_child else []
    assert parent_state["paths"] == expected_paths


def test_pihc3_doctrine_diagram_rolls_back_new_module_on_build_rejection(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _write_doctrine_authoring_project(tmp_path)
    request = {
        "doctrine_id": "DOCTRINE_TEST_REJECTED",
        "title": "拒绝教义",
        "parent_doctrine_id": "DOCTRINE_TEST_SUCCESSOR",
    }
    plan = project.edit_module_diagram("doctrine", node_intents=[request])
    parent_state = project.root / "src/modules/doctrine/DOCTRINE_TEST_SUCCESSOR - 后续教义/" ".paradev/diagram.yaml"
    original_parent_state = parent_state.read_bytes()

    def rejected_build(
        _project: Project,
        **_options: object,
    ) -> BuildResult:
        return BuildResult.plan(
            "doctrine",
            profile="hoi4",
            diagnostics=(
                Diagnostic(
                    code="test.doctrine_build_rejected",
                    message="Synthetic project-local Doctrine build rejection.",
                ),
            ),
        )

    monkeypatch.setattr(Project, "build", rejected_build)
    rejected = project.edit_module_diagram(
        "doctrine",
        node_intents=[request],
        write=True,
        plan_hash=plan["plan_hash"],
    )

    assert rejected["blocked"] is True
    assert rejected["written"] is False
    assert any(row["code"] == "module_diagram.build_rejected" for row in rejected["diagnostics"])
    assert not (project.root / "src/modules/doctrine/DOCTRINE_TEST_REJECTED - 拒绝教义").exists()
    assert parent_state.read_bytes() == original_parent_state


def test_pihc3_doctrine_diagram_rolls_back_child_on_parent_source_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _write_doctrine_authoring_project(tmp_path)
    request = {
        "doctrine_id": "DOCTRINE_TEST_CONFLICT",
        "title": "冲突教义",
        "parent_doctrine_id": "DOCTRINE_TEST_SUCCESSOR",
    }
    plan = project.edit_module_diagram("doctrine", node_intents=[request])
    parent_state = project.root / "src/modules/doctrine/DOCTRINE_TEST_SUCCESSOR - 后续教义/" ".paradev/diagram.yaml"
    original_parent_state = parent_state.read_bytes()

    def rejected_source_mutation(*_args: object, **_kwargs: object) -> None:
        raise ValueError("Synthetic parent source conflict.")

    monkeypatch.setattr(
        "paradev.sdk.project._apply_source_draft_mutations",
        rejected_source_mutation,
    )
    rejected = project.edit_module_diagram(
        "doctrine",
        node_intents=[request],
        write=True,
        plan_hash=plan["plan_hash"],
    )

    assert rejected["blocked"] is True
    assert rejected["written"] is False
    assert any(row["code"] == "module_diagram.source_conflict" for row in rejected["diagnostics"])
    assert not (project.root / "src/modules/doctrine/DOCTRINE_TEST_CONFLICT - 冲突教义").exists()
    assert parent_state.read_bytes() == original_parent_state


def test_pihc3_doctrine_diagram_rejects_stale_parent_source_context(
    tmp_path: Path,
) -> None:
    project = _write_doctrine_authoring_project(tmp_path)
    request = {
        "doctrine_id": "DOCTRINE_TEST_STALE",
        "title": "过期教义",
        "parent_doctrine_id": "DOCTRINE_TEST_SUCCESSOR",
    }
    plan = project.edit_module_diagram("doctrine", node_intents=[request])
    successor_state = project.root / "src/modules/doctrine/DOCTRINE_TEST_SUCCESSOR - 后续教义/" ".paradev/diagram.yaml"
    state = yaml.safe_load(successor_state.read_text(encoding="utf-8"))
    state["position"]["x"] = 4
    successor_state.write_text(
        yaml.safe_dump(state, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )

    stale = project.edit_module_diagram(
        "doctrine",
        node_intents=[request],
        write=True,
        plan_hash=plan["plan_hash"],
    )

    assert stale["blocked"] is True
    assert stale["written"] is False
    assert any(row["code"] == "module_diagram.plan_hash_mismatch" for row in stale["diagnostics"])
    assert not (project.root / "src/modules/doctrine/DOCTRINE_TEST_STALE - 过期教义").exists()
