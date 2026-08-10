"""PIHC3 compatibility contracts for HOI4 1.19 Army Headquarters."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from paradev.sdk import Project

PROJECT_ROOT = Path("projects/PIHC3")


def _module_root(family: str, object_id: str) -> Path:
    matches = tuple((PROJECT_ROOT / "src/modules" / family).glob(f"{object_id} - *"))
    assert len(matches) == 1
    return matches[0]


HQ_UNIT_PATH = _module_root("unit", "UNIT_UNITS_HQ_SUPPORT") / "common/units/hq_support.txt"
HQ_TEMPLATE_PATH = _module_root("general_history", "GENERAL_HISTORY_GENERAL_TAOG_HQ_TEMPLATE") / "history/general/taog_hq_template.txt"
HQ_AI_PATH = _module_root("ai_config", "AI_CONFIG_AI_TEMPLATES_HQ_SUPPORT") / "common/ai_templates/hq_support.txt"


def test_pihc3_restores_default_army_hq_inputs_hidden_by_replace_paths() -> None:
    project = Project.load(PROJECT_ROOT)
    registry = project._build_registry(profile=project.game)
    replace_paths = project.descriptor_metadata["replace_path"]
    assert "common/units" in replace_paths
    assert "history/general" in replace_paths

    assert any("common/units" in slot.match for slot in registry.source_slots_for("unit"))
    assert HQ_UNIT_PATH.is_file()
    assert HQ_TEMPLATE_PATH.is_file()
    assert HQ_AI_PATH.is_file()

    game_asset_slots = registry.source_slots_for("game_asset")
    assert any("common/achievements" in slot.match for slot in game_asset_slots)


def test_pihc3_default_army_hq_uses_defined_pihc_equipment() -> None:
    unit_text = HQ_UNIT_PATH.read_text(encoding="utf-8")
    template_text = HQ_TEMPLATE_PATH.read_text(encoding="utf-8")

    for subunit in ("hq_support_company", "hq_infantry"):
        assert f"{subunit} = {{" in unit_text
        assert f"{subunit} = {{" in template_text
    assert "allow_in_army_hq = yes" in unit_text
    assert "allow_in_non_army_hq = no" in unit_text
    assert 'required_dlc = { "Thunder at Our Gates" }' in unit_text
    assert "ARCHETYPE_INFANTRY" in unit_text
    for unavailable_equipment in ("infantry_equipment", "support_equipment", "motorized_equipment"):
        assert f"{unavailable_equipment} =" not in unit_text

    assert "every_possible_country = {" in template_text
    assert 'has_dlc = "Thunder at Our Gates"' in template_text
    assert 'localization_key = "ARMY_HQ_TEMPLATE_NAME"' in template_text
    assert "template_counter = 121" in template_text
    assert "is_army_hq = yes" in template_text


def test_pihc3_startup_checker_enforces_army_hq_source_and_output_contracts(tmp_path: Path) -> None:
    script_path = PROJECT_ROOT / "scripts/check_startup_error_contracts.py"
    spec = importlib.util.spec_from_file_location("check_startup_error_contracts", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    source_errors: list[str] = []
    module.check_source(PROJECT_ROOT, source_errors)
    assert not [error for error in source_errors if "Army HQ" in error]

    output_errors: list[str] = []
    module.check_army_hq_contracts(HQ_UNIT_PATH, HQ_TEMPLATE_PATH, HQ_AI_PATH, output_errors, label="test")
    assert output_errors == []

    missing_errors: list[str] = []
    module.check_army_hq_contracts(
        tmp_path / "common/units/hq_support.txt",
        tmp_path / "history/general/taog_hq_template.txt",
        tmp_path / "common/ai_templates/hq_support.txt",
        missing_errors,
        label="compiled output",
    )
    assert missing_errors == [f"compiled output Army HQ subunit definitions are missing: {tmp_path.as_posix()}/common/units/hq_support.txt"]

    adjacency_path = tmp_path / "map/adjacencies.csv"
    adjacency_path.parent.mkdir(parents=True)
    adjacency_path.write_text(
        "From;To;Type;Through;start_x;start_y;stop_x;stop_y;adjacency_rule_name;Comment\n" "10;20;sea;10;-1;-1;-1;-1;;invalid\n" "-1;-1;;-1;-1;-1;-1;-1;-1\n",
        encoding="utf-8",
    )
    adjacency_errors: list[str] = []
    module.check_map_adjacencies(adjacency_path, adjacency_errors, label="test")
    assert adjacency_errors == ["test map adjacencies use an endpoint as Through: line 2 (10->20 through 10)"]

    achievements_path = tmp_path / "common/achievements.txt"
    achievements_path.parent.mkdir(parents=True, exist_ok=True)
    achievements_path.write_text(
        f"# {module.VANILLA_ACHIEVEMENTS_OVERRIDE_MARKER}\nachievements = {{}}\n",
        encoding="utf-8",
    )
    achievements_errors: list[str] = []
    module.check_vanilla_achievements_override(achievements_path, achievements_errors, label="test")
    assert achievements_errors == [f"test vanilla achievements override must remain comment-only: {achievements_path.as_posix()}"]
