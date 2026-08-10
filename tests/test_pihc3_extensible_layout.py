from __future__ import annotations

import json
import os
import subprocess
from collections import Counter
from pathlib import Path

import heavenbase as hb
import pytest
from heavenbase.utils import load_yaml

from paradev.config import _CONTEXT_PARADEV
from paradev.sdk import Project
from paradev.sdk.source_forms import loc_text_source_form

pytestmark = pytest.mark.integration

PIHC3_ROOT = Path("projects/PIHC3").resolve()
SOURCE_ROOT = PIHC3_ROOT / "src"
VISIBLE_METADATA_KEYS = frozenset({"collection", "inactive", "comment"})
HIDDEN_COLLECTION_FAMILIES = frozenset({"focus", "modifier"})
FAMILY_PRESENTATION_GROUPS = {
    "country",
    "military",
    "world",
    "events",
    "shared",
    "other",
}
BUILTIN_COMPILER_OVERLAYS = {
    "decision": "pihc3-decision",
    "event": "pihc3-event",
    "focus": "pihc3-focus",
    "idea": "pihc3-idea",
    "modifier": "pihc3-modifier",
    "opinion_modifier": "pihc3-opinion-modifier-module",
    "trait": "pihc3-trait-module",
}


def _extension_descriptor(extension_root: Path) -> Path:
    return extension_root / ".paradev/meta.yaml"


def _source_units() -> tuple[Path, ...]:
    return tuple(
        unit
        for kind in ("modules", "collections")
        for family_root in sorted(path for path in (SOURCE_ROOT / kind).iterdir() if path.is_dir())
        for unit in sorted(path for path in family_root.iterdir() if path.is_dir())
    )


def _live_project_directories() -> tuple[Path, ...]:
    directories: list[Path] = []
    for root, names, _files in os.walk(PIHC3_ROOT):
        names[:] = [name for name in names if name != ".git"]
        directories.extend(Path(root, name) for name in names)
    return tuple(directories)


def test_pihc3_source_tree_uses_one_clean_semantic_layout() -> None:
    units = _source_units()
    extension_roots = tuple(path for path in (PIHC3_ROOT / "extensions").iterdir() if path.is_dir() and not path.name.startswith("."))
    live_directories = _live_project_directories()

    assert units
    assert len(extension_roots) == 71
    assert all(not (root / "meta.yaml").exists() for root in extension_roots)
    assert all(_extension_descriptor(root).is_file() for root in extension_roots)
    assert not [path for path in live_directories if path.name.casefold() == "inactive_modules" or "legacy" in path.name.casefold()]
    assert not [path for path in SOURCE_ROOT.rglob("*") if path.is_file() and "legacy" in path.name.casefold()]
    assert not list(SOURCE_ROOT.rglob("legacy-source.yaml"))
    assert not [path for path in live_directories if "_asset_component" in path.name.casefold() or path.name.casefold().endswith("_component")]
    assert all(" - " in unit.name for unit in units)
    assert not list((SOURCE_ROOT / "modules/decision").glob("*/meta.yaml"))
    assert [unit / "meta.yaml" for unit in units if (unit / "meta.yaml").is_file()] == [SOURCE_ROOT / "modules/bookmark/PIHC_DIE_NEBENWELT - 新世界/meta.yaml"]
    hidden_metadata_paths = tuple(unit / ".paradev/meta.yaml" for unit in units if (unit / ".paradev/meta.yaml").is_file())
    assert Counter(path.parents[2].name for path in hidden_metadata_paths) == {
        "focus": 738,
        "modifier": 109,
    }

    for unit in units:
        visible_path = unit / "meta.yaml"
        if visible_path.is_file():
            metadata = load_yaml(str(visible_path), strict=True)
            assert isinstance(metadata, dict)
            assert set(metadata) <= VISIBLE_METADATA_KEYS

        hidden_path = unit / ".paradev/meta.yaml"
        if not hidden_path.is_file():
            continue
        metadata = load_yaml(str(hidden_path), strict=True)
        assert isinstance(metadata, dict)
        assert set(metadata) <= {"collection", "settings"}
        collection = metadata.get("collection")
        if collection is not None:
            assert unit.parent.name in HIDDEN_COLLECTION_FAMILIES
            assert isinstance(collection, str) and collection
        settings = metadata.get("settings")
        assert settings is None
        rendered = hidden_path.read_text(encoding="utf-8")
        assert "legacy_" not in rendered
        assert "/Users/" not in rendered


def test_pihc3_entity_families_are_registry_loaded_from_project_code() -> None:
    project = Project.load(PIHC3_ROOT)
    registry = project._build_registry(profile=project.game)
    resolver = _CONTEXT_PARADEV.modules()
    entity_count = 0
    compiler_overlays: list[str] = []
    auxiliary_bundles: list[tuple[str, tuple[str, ...]]] = []

    for extension_root in sorted(path for path in (PIHC3_ROOT / "extensions").iterdir() if path.is_dir() and not path.name.startswith(".")):
        descriptor = load_yaml(
            str(_extension_descriptor(extension_root)),
            strict=True,
        )
        assert isinstance(descriptor, dict)
        items = descriptor["items"]
        entity_items = [item for item in items if isinstance(item, dict) and item.get("kind") == "entity"]
        family_items = [item for item in items if isinstance(item, dict) and item.get("kind") == "paradev_build_family"]
        if not entity_items:
            if family_items:
                assert extension_root.name in BUILTIN_COMPILER_OVERLAYS
                assert len(family_items) == 1
                item_kinds = [item["kind"] for item in items if isinstance(item, dict)]
                assert item_kinds[0] == "paradev_build_family"
                assert not {"entity", "extension"}.intersection(item_kinds)
                family_item = family_items[0]
                family_target = resolver.resolve(
                    "paradev_build_family",
                    family_item["identifier"],
                )
                assert callable(family_target)
                built_family = family_target()
                registered_family = registry.family(extension_root.name)
                assert built_family.family == extension_root.name
                assert tuple(built_family.source_slots) == tuple(registered_family.source_slots)
                assert type(built_family) is type(registered_family)
                with pytest.raises(KeyError, match="Unknown system module"):
                    resolver.resolve(
                        "entity",
                        BUILTIN_COMPILER_OVERLAYS[extension_root.name],
                    )
                compiler_overlays.append(extension_root.name)
                continue
            auxiliary_bundles.append(
                (
                    extension_root.name,
                    tuple(str(item["kind"]) for item in items if isinstance(item, dict)),
                )
            )
            continue

        entity_count += 1
        assert len(entity_items) == 1, extension_root.name
        assert len(family_items) == 1, extension_root.name
        entity_item = entity_items[0]
        entity_target = entity_item["target"]
        assert entity_item["source"] == "path"
        assert isinstance(entity_target, dict)
        assert entity_target["module"] is None
        assert isinstance(entity_target["qualname"], str)
        assert "definition" not in entity_item["meta"]

        entity_class = resolver.resolve("entity", entity_item["identifier"])
        assert isinstance(entity_class, type)
        assert issubclass(entity_class, hb.Entity)
        assert entity_class.__module__.startswith("_heavenbase_artifact_")
        assert entity_class.identifier == entity_item["identifier"]
        assert entity_class.schema().entity_id == entity_item["identifier"]
        assert set(entity_class.schema().fields).difference({"object_id"})
        assert entity_class.family == extension_root.name
        assert tuple(entity_class.resource_slots)
        assert {"normalize", "check", "emit"}.issubset(entity_class.compilation_hooks)
        assert tuple(registry.source_slots_for(entity_class.family)) == tuple(entity_class.resource_slots)

        family_item = family_items[0]
        family_target = resolver.resolve(
            "paradev_build_family",
            family_item["identifier"],
        )
        assert callable(family_target)
        assert family_target.__module__.startswith("_heavenbase_artifact_")
        built_family = family_target()
        registered_family = registry.family(entity_class.family)
        assert built_family.family == entity_class.family
        assert tuple(built_family.source_slots) == tuple(entity_class.resource_slots)
        assert type(built_family) is type(registered_family)

    assert entity_count == 63
    assert compiler_overlays == sorted(BUILTIN_COMPILER_OVERLAYS)
    assert auxiliary_bundles == [
        (
            "localisation",
            ("paradev_build_writer", "paradev_build_postprocessor"),
        )
    ]


def test_pihc3_hidden_extension_descriptors_are_versionable() -> None:
    if not (PIHC3_ROOT / ".git").exists():
        pytest.skip("PIHC3 Git metadata is unavailable")

    for metadata_path in (
        "extensions/achievement/.paradev/meta.yaml",
        ("src/modules/focus/" "FOCUS_C01_C02_EVERFREE_FIELDTRIP - 无尽之森旅行/" ".paradev/meta.yaml"),
        ("src/modules/modifier/" "active_decryption_modifier - 利用已破译的敌方密码获取全部情报/" ".paradev/meta.yaml"),
    ):
        result = subprocess.run(
            (
                "git",
                "check-ignore",
                "--quiet",
                "--no-index",
                metadata_path,
            ),
            cwd=PIHC3_ROOT,
            check=False,
        )

        assert result.returncode == 1, metadata_path


@pytest.mark.parametrize(
    ("module_id", "target_id"),
    (
        (
            "focus/FOCUS_C01_C02_EVERFREE_FIELDTRIP",
            "PARADEV_TEST_FOCUS_COPY",
        ),
        (
            "modifier/active_decryption_modifier",
            "paradev_test_modifier_copy",
        ),
    ),
)
def test_pihc3_duplicate_plan_preserves_hidden_family_routing(
    module_id: str,
    target_id: str,
) -> None:
    plan = Project.load(PIHC3_ROOT).duplicate_module(module_id, target_id)

    assert plan["blocked"] is False
    system_metadata = [row for row in plan["files"] if row["relative_path"] == ".paradev/meta.yaml"]
    assert len(system_metadata) == 1
    assert system_metadata[0]["action"] == "copy"
    assert not [row for row in plan["exclusions"] if row["relative_path"] == ".paradev"]


def test_pihc3_titled_folders_prefer_chinese_name_localization() -> None:
    intelligence_root = SOURCE_ROOT / "modules/intelligence_agency"
    intelligence_titles = {path.name.split(" - ", 1)[0]: path.name.split(" - ", 1)[1] for path in intelligence_root.iterdir() if path.is_dir()}

    assert intelligence_titles == {
        "INTEL_AGENCY_BOC": "水晶之锋",
        "INTEL_AGENCY_CECIA": "幻形灵帝国中央情报局",
        "INTEL_AGENCY_DDDPPPWWWHHH": ("Die Die Die Pie Pie Pie Why Why Why Hi Hi Hi"),
        "INTEL_AGENCY_DEFAULT": "情报机关",
        "INTEL_AGENCY_EEMO": "小马利亚帝国国家安全部",
        "INTEL_AGENCY_EOF": "恐惧之眼",
        "INTEL_AGENCY_LFCC": "骆驼桥学院",
        "INTEL_AGENCY_MNS": "国家安全部",
        "INTEL_AGENCY_SEPAL": "萼叶组织",
    }
    assert (SOURCE_ROOT / "modules/country/C66 - 火驽鲁鲁共和国").is_dir()


def test_pihc3_registry_uses_project_extensions_for_core_authoring() -> None:
    project = Project.load(PIHC3_ROOT)
    registry = project._build_registry(profile=project.game)
    expected_families = {
        "achievement": "PIHC3AchievementFamily",
        "character": "PIHC3CharacterFamily",
        "country": "PIHC3CountryFamily",
        "decision": "PIHC3DecisionFamily",
        "division": "PIHC3DivisionFamily",
        "doctrine": "PIHC3DoctrineFamily",
        "event": "PIHC3EventFamily",
        "focus": "PIHC3FocusFamily",
        "idea": "PIHC3IdeaFamily",
        "idea_category": "PIHC3IdeaCategoryFamily",
        "military_industrial_organization": ("PIHC3MilitaryIndustrialOrganizationFamily"),
        "modifier": "PIHC3ModifierFamily",
        "opinion_modifier": "PIHC3OpinionModifierFamily",
        "state": "PIHC3StateFamily",
        "technology": "PIHC3TechnologyFamily",
        "trait": "PIHC3TraitFamily",
    }

    for family_id, class_name in expected_families.items():
        family = registry.family(family_id)
        assert family.__class__.__name__ == class_name
        assert registry.source_slots_for(family_id)
        assert not hasattr(family, "retired_families")

    assert all(registry.publication_replacements_for(family.family) == () for family in registry.families)
    assert all("publication" not in row and "replaces_families" not in row for row in registry.to_view()["families"])

    for retired_family in (
        "decision_support",
        "decision_asset_component",
        "event_asset_component",
        "event_component",
        "flag_asset_component",
        "focus_asset_component",
        "focus_tree",
        "idea_support",
        "idea_asset_component",
        "military_industrial_organization_component",
        "special_project_support",
        "technology_support",
        "texticon_asset_component",
        "ui_asset_component",
    ):
        with pytest.raises(ValueError, match="not registered"):
            registry.family(retired_family)


def test_pihc3_browser_exposes_registry_resource_ownership_for_authoring() -> None:
    project = Project.load(PIHC3_ROOT)
    [technology] = project.browser(
        kind="module",
        family="technology",
        module_id="technology/TECHNOLOGY_AIR_AIRSHIP",
    )["items"]

    compiled_assets = [row for row in technology["resource_slots"] if row["name"] == "compiled_assets"]
    assert {(row["match"], row["kind"], row["authoring_path"]) for row in compiled_assets} == {
        (
            r"^gfx/interface/technologies/.*\.dds$",
            "copy",
            "gfx/interface/technologies/{filename}",
        ),
        (
            r"^interface/technologies/.*\.gfx$",
            "copy",
            "interface/technologies/{filename}",
        ),
    }
    owned_sources = [row for row in technology["sources"] if row["slot"] == "compiled_assets"]
    assert owned_sources
    assert all(row["slot_kinds"] == ["copy"] for row in owned_sources)


def test_major_pihc3_entities_declare_safe_copy_authoring_destinations() -> None:
    registry = Project.load(PIHC3_ROOT)._build_registry(profile="hoi4")
    authorable_families = {
        "achievement",
        "character",
        "country",
        "decision",
        "entity",
        "equipment",
        "equipment_module",
        "event",
        "focus",
        "idea",
        "idea_category",
        "inventory_item",
        "modifier",
        "opinion_modifier",
        "special_project",
        "superevent",
        "technology",
        "trait",
    }

    for family_id in sorted(authorable_families):
        copy_slots = [slot for slot in registry.source_slots_for(family_id) if slot.kind == "copy"]
        assert copy_slots, family_id
        assert all(slot.authoring_path for slot in copy_slots), family_id


def test_pihc3_build_extensions_own_desktop_presentation_capabilities() -> None:
    descriptor_presentations: dict[str, dict[str, object]] = {}
    build_item_count = 0
    for extension_root in sorted(path for path in (PIHC3_ROOT / "extensions").iterdir() if path.is_dir() and not path.name.startswith(".")):
        descriptor = load_yaml(
            str(_extension_descriptor(extension_root)),
            strict=True,
        )
        assert isinstance(descriptor, dict)
        for item in descriptor["items"]:
            if not isinstance(item, dict) or item.get("kind") != "paradev_build_family":
                continue
            build_item_count += 1
            assert item.get("source") == "path"
            target = item.get("target")
            assert isinstance(target, dict)
            assert isinstance(target.get("qualname"), str)
            meta = item["meta"]
            assert isinstance(meta, dict)
            assert "definition" not in meta
            presentation = meta.get("presentation")
            assert isinstance(presentation, dict)
            assert set(presentation) <= {
                "id",
                "title",
                "group",
                "aliases",
                "title_key",
            }
            assert isinstance(presentation.get("id"), str)
            assert isinstance(presentation.get("title"), str)
            assert presentation.get("group") in FAMILY_PRESENTATION_GROUPS
            descriptor_presentations[extension_root.name] = presentation

    assert build_item_count == 70
    assert len(descriptor_presentations) == 70

    project = Project.load(PIHC3_ROOT)
    registry = project._build_registry(profile=project.game)
    presentations = registry.presentation_views_by_family()
    presentation_ids = [str(row["id"]) for row in presentations.values()]

    assert len(presentation_ids) == len(set(presentation_ids))
    assert presentations["focus"] == {
        "id": "focuses",
        "title": "Focuses",
        "group": "country",
        "title_key": "modules.focuses.title",
    }
    assert presentations["military_industrial_organization"] == {
        "id": "military-industrial-organizations",
        "title": "Military Industrial Organizations",
        "group": "military",
        "aliases": ["mio"],
        "title_key": "modules.militaryIndustrialOrganizations.title",
    }
    assert registry.resolve_family("focuses") == "focus"
    assert registry.resolve_family("mio") == "military_industrial_organization"

    browser_families = {row["id"]: row for row in project.browser_summary()["families"]}
    assert browser_families["inventory-items"]["group"] == "events"
    assert browser_families["inventory-items"]["title_key"] == "modules.inventoryItems.title"
    assert browser_families["ai-config"]["visible"] is False


def test_pihc3_tree_families_replace_profile_diagram_providers_through_heavenbase() -> None:
    project = Project.load(PIHC3_ROOT)
    registry = project._build_registry(profile=project.game)
    expected = {
        "doctrine": ("doctrine", "doctrine"),
        "focus": ("focus_tree", "focus-tree"),
        "military_industrial_organization": (
            "military_industrial_organization",
            "mio-trait",
        ),
        "technology": ("technology", "technology"),
    }

    assert all(provider.replaces_registered_provider for provider in registry.diagram_providers)
    for family, (identifier, renderer) in expected.items():
        capability = registry.diagram_views_by_family()[family]
        assert capability["id"] == identifier
        assert capability["renderer"] == renderer
        descriptor = load_yaml(
            str(_extension_descriptor(PIHC3_ROOT / "extensions" / family)),
            strict=True,
        )
        assert isinstance(descriptor, dict)
        items = descriptor["items"]
        assert any(isinstance(row, dict) and row.get("kind") == "paradev_diagram_provider" for row in items)


def test_pihc3_visible_scripted_families_own_guided_source_contracts() -> None:
    project = Project.load(PIHC3_ROOT)
    registry = project._build_registry(profile=project.game)
    visible_families = {str(row["family"]) for row in project.browser_summary(registry=registry)["families"] if row.get("visible", True)}
    guided_families = {
        family
        for family in visible_families
        if callable(getattr(registry.family(family), "source_form", None)) or any(slot.kind == "pdx" for slot in registry.source_slots_for(family))
    }

    assert len(visible_families) == 51
    assert len(guided_families) == 50
    assert visible_families - guided_families == {"equipment_module_category"}
    for family in (
        "decision",
        "division",
        "entity",
        "event",
        "idea",
        "military_industrial_organization",
        "opinion_modifier",
        "portrait",
        "state_lore",
        "texticon",
        "trait",
        "ui",
    ):
        assert any(slot.kind == "pdx" for slot in registry.source_slots_for(family))
    inventory_family = registry.family("inventory_item")
    assert callable(getattr(inventory_family, "source_form", None))
    assert any(slot.name == "definition" and slot.match == "item.json" for slot in registry.source_slots_for("inventory_item"))


def test_pihc3_high_traffic_entities_own_real_module_edit_help() -> None:
    project = Project.load(PIHC3_ROOT)
    registry = project._build_registry(profile=project.game)
    samples = {
        "idea": (
            "IDEA_ALL_ARTIFACT_CROWN_OF_GROVER - 发现法器：格罗弗皇冠/def.txt",
            "removal_cost",
        ),
        "character": ("CHARACTER_TREE_HUGGER - 树之怀/def.txt", "gender"),
        "focus": ("FOCUS_C12_SHADOWS_OF_THE_PAST - 往日的阴影/def.txt", "cost"),
        "technology": ("TECHNOLOGY_TECH_MAGI - 魔法技术/def.txt", "research_cost"),
        "decision": ("DECISION_C01_C03_PUPPET - 傀儡云中城/def.txt", "days_remove"),
        "event": ("C22_MAIN - 狮鹫的荣耀/def.txt", "is_triggered_only"),
        "equipment": (
            "EQUIPMENT_CANNON_HEAVY_MODERN - 重型近代加农炮 (重型加农炮)/def.txt",
            "build_cost_ic",
        ),
        "country": ("C13 - 禁区丛林/def.txt", "graphical_culture"),
    }

    for family_id, (relative_path, expected_key) in samples.items():
        family = registry.family(family_id)
        hints = getattr(family, "source_form_field_hints", None)
        assert isinstance(hints, dict) and expected_key in hints
        form = project.source_form(SOURCE_ROOT / "modules" / family_id / relative_path)
        assert form is not None
        controls: list[dict[str, object]] = []
        stack = list(form["sections"])
        while stack:
            section = stack.pop()
            assert isinstance(section, dict)
            controls.extend(section.get("controls", []))
            stack.extend(section.get("sections", []))
        declared = [
            control
            for control in controls
            if control.get("description_source") == "declared"
            and isinstance(control.get("patch"), dict)
            and control["patch"]["path"][-1]["key"] == expected_key
        ]
        assert declared, family_id
        assert all(control.get("description") for control in controls)

    event_form = project.source_form(SOURCE_ROOT / "modules/event" / samples["event"][0])
    assert event_form is not None
    assert event_form["coverage"]["truncated"] is True
    assert event_form["coverage"]["shown_controls"] < event_form["coverage"]["total_controls"]

    event_query = "C01_C02_GREENLIGHT.40"
    event_path = SOURCE_ROOT / "modules/event" / "C01_C02_GREENLIGHT - 「绿灯」行动报告：疯狂杜鹃" / "def.txt"
    queried_event_form = project.source_form(event_path, query=event_query)
    assert queried_event_form is not None
    assert queried_event_form["query"] == event_query
    assert queried_event_form["coverage"] == {
        "truncated": False,
        "shown_controls": 14,
        "total_controls": 14,
    }
    assert any(event_query in str(section["label"]) for section in queried_event_form["sections"])
    queried_controls = [control for section in queried_event_form["sections"] for control in section.get("controls", [])]
    title_control = next(control for control in queried_controls if control["patch"]["path"][-1]["key"] == "title")
    assert title_control["id"] == "pdx-control-377"
    update = project.plan_source_form_update(
        event_path,
        {title_control["id"]: "EVENT_C01_C02_GREENLIGHT_40_REVISED"},
        query=event_query,
    )
    assert "title = EVENT_C01_C02_GREENLIGHT_40_REVISED" in update["source_edit"]["text"]
    assert event_path.read_text(encoding="utf-8") not in {"", update["source_edit"]["text"]}


def test_pihc3_mio_extension_owns_guided_tree_and_bonus_help() -> None:
    project = Project.load(PIHC3_ROOT)
    registry = project._build_registry(profile=project.game)
    family = registry.family("military_industrial_organization")
    hints = getattr(family, "source_form_field_hints", None)

    assert isinstance(hints, dict)
    assert {
        "all_parents",
        "any_parent",
        "equipment_bonus",
        "equipment_type",
        "name",
        "relative_position_id",
        "token",
        "x",
        "y",
    } <= set(hints)

    source_path = (
        SOURCE_ROOT
        / "modules/military_industrial_organization"
        / "c01_airship_organization - C01飞艇军工组织"
        / "common/military_industrial_organization/organizations/C01.txt"
    )
    form = project.source_form(source_path)
    assert form is not None
    controls: list[dict[str, object]] = []
    stack = list(form["sections"])
    while stack:
        section = stack.pop()
        assert isinstance(section, dict)
        controls.extend(section.get("controls", []))
        stack.extend(section.get("sections", []))

    declared_by_key: dict[str, list[dict[str, object]]] = {}
    for control in controls:
        patch = control.get("patch")
        if control.get("description_source") != "declared" or not isinstance(patch, dict):
            continue
        path = patch.get("path")
        if not isinstance(path, list) or not path or not isinstance(path[-1], dict):
            continue
        declared_by_key.setdefault(str(path[-1].get("key")), []).append(control)

    assert {
        "any_parent",
        "equipment_bonus",
        "name",
        "relative_position_id",
        "token",
        "x",
        "y",
    } <= set(declared_by_key)
    assert hints["all_parents"]["control"] == "block-text"
    assert hints["all_parents"]["label"] == {
        "default": "Required parent traits",
        "zh": "必需父特质",
    }
    assert declared_by_key["any_parent"][0]["control"] == "text"
    assert declared_by_key["any_parent"][0]["multiline"] is True
    assert declared_by_key["equipment_bonus"][0]["control"] == "text"
    assert declared_by_key["equipment_bonus"][0]["multiline"] is True
    assert declared_by_key["token"][0]["label"] == {
        "default": "Trait token",
        "zh": "特质标识",
    }
    assert declared_by_key["relative_position_id"][0]["description"] == {
        "default": "Trait token used as the relative-position anchor for this node.",
        "zh": "作为此节点相对位置锚点的特质标识。",
    }


def test_pihc3_requested_semantic_families_own_guided_existing_source_help() -> None:
    project = Project.load(PIHC3_ROOT)
    registry = project._build_registry(profile=project.game)
    modules_root = SOURCE_ROOT / "modules"
    state_lore_root = next((modules_root / "state_lore").glob("STATE_LORE_217 - *"))
    cases = {
        "achievement": {
            "paths": (modules_root / "achievement/ACHIEVEMENT_PIHC_1CO_ALL_THE_FIRST_GAME - 第一印象/def.txt",),
            "hint_keys": {"happened", "possible", "unique_id"},
            "control_keys": {"happened", "possible", "unique_id"},
        },
        "division": {
            "paths": (
                modules_root / "division/C00 - PIHC2 C00 Divisions/history/units/C00.txt",
                modules_root / ("division/C00 - PIHC2 C00 Divisions/" "common/units/names_divisions/C00.txt"),
            ),
            "hint_keys": {"division_types", "name", "regiments", "support"},
            "control_keys": {"division_types", "name", "regiments", "support"},
        },
        "doctrine": {
            "paths": (modules_root / "doctrine/DOCTRINE_AIR_0_0_OPEN_SKY - 开放天空/def.txt",),
            "hint_keys": {"ai_will_do", "available", "milestones", "xp_cost"},
            "control_keys": {"ai_will_do", "available", "milestones", "xp_cost"},
        },
        "modifier": {
            "paths": (modules_root / ("modifier/BOP_C01_COZY_GLOW_EXHAUSTION_DAILY_COST - " "Daily Tiredness/def.txt"),),
            "hint_keys": {"$root"},
            "control_keys": {"BOP_C01_COZY_GLOW_EXHAUSTION_DAILY_COST"},
        },
        "inventory_item": {
            "paths": (modules_root / ("inventory_item/1CO_C22_C07_TICKET_FINE - " "世界博览会·蒸汽机会场·门票罚款/item.json"),),
            "hint_keys": set(),
            "control_keys": {"helper_quantities"},
        },
        "state_lore": {
            "paths": (state_lore_root / "variants.pdx",),
            "hint_keys": {"localization_key", "trigger", "variant"},
            "control_keys": {"localization_key", "trigger"},
        },
        "superevent": {
            "paths": (modules_root / ("superevent/1 - 亵渎水晶的小马有难了，" "因为水晶帝国的大门将对他们紧闭。/def.txt"),),
            "hint_keys": {"id", "immediate", "option", "picture"},
            "control_keys": {"id", "immediate", "option", "picture"},
        },
    }

    assert registry.family("inventory_item").__class__.__name__ == ("PIHC3InventoryItemFamily")
    assert registry.family("superevent").__class__.__name__ == ("PIHC3SupereventFamily")

    for family_id, case in cases.items():
        family = registry.family(family_id)
        hints = getattr(family, "source_form_field_hints", None)
        if case["hint_keys"]:
            assert isinstance(hints, dict)
            assert case["hint_keys"] <= set(hints)
        else:
            assert callable(getattr(family, "source_form", None))
        declared_controls: list[dict[str, object]] = []
        source_snapshots: dict[Path, str] = {}
        block_probe: tuple[Path, dict[str, object]] | None = None
        json_probe: tuple[Path, dict[str, object]] | None = None

        for source_path in case["paths"]:
            source_snapshots[source_path] = source_path.read_text(encoding="utf-8")
            form = project.source_form(source_path)
            assert form is not None
            controls: list[dict[str, object]] = []
            stack = list(form["sections"])
            while stack:
                section = stack.pop()
                assert isinstance(section, dict)
                controls.extend(section.get("controls", []))
                stack.extend(section.get("sections", []))
            for control in controls:
                if control.get("description_source") != "declared":
                    continue
                declared_controls.append(control)
                if block_probe is None and control["patch"]["op"] == "replace-pdx-block-body":
                    block_probe = (source_path, control)
                if json_probe is None and control["patch"]["op"] == "replace-json-scalar":
                    json_probe = (source_path, control)

        declared_keys = {
            str(control["patch"]["path"][-1] if control["patch"]["op"] == "replace-json-scalar" else control["patch"]["path"][-1]["key"])
            for control in declared_controls
        }
        assert case["control_keys"] <= declared_keys
        assert all(control.get("label") for control in declared_controls)
        assert all(control.get("description") for control in declared_controls)

        if json_probe is not None:
            source_path, control = json_probe
            plan = project.plan_source_form_update(
                source_path,
                {control["id"]: "1-2"},
            )
            assert plan["changed"] is True
        else:
            assert block_probe is not None
            source_path, block_control = block_probe
            plan = project.plan_source_form_update(
                source_path,
                {block_control["id"]: f"{block_control['value']}\n# Guided help probe"},
            )
            assert plan["changed"] is True
        assert all(path.read_text(encoding="utf-8") == source_text for path, source_text in source_snapshots.items())

    inventory_form = project.source_form(cases["inventory_item"]["paths"][0])
    assert inventory_form is not None
    assert inventory_form["source_format"] == "json"
    assert inventory_form["contract"] == "pihc3.inventory-item.definition.v1"
    assert inventory_form["sections"][0]["controls"][0]["id"] == ("helper_quantities")
    with pytest.raises(ValueError, match="must not exceed 99999"):
        registry.family("inventory_item").validate_source_text(
            module_id="inventory_item/1CO_C22_C07_TICKET_FINE",
            relative_path="item.json",
            text='{"helper_quantities": "1, 100000"}\n',
        )


def test_pihc3_visible_families_publish_complete_authoring_capabilities() -> None:
    project = Project.load(PIHC3_ROOT)
    registry = project._build_registry(profile=project.game)
    visible_families = {str(row["family"]) for row in project.browser_summary(registry=registry)["families"] if row.get("visible", True)}
    templates = project.templates(
        authoring_ready=True,
        source="project",
    )["templates"]
    templates_by_family: dict[str, list[dict[str, object]]] = {}
    for template in templates:
        templates_by_family.setdefault(str(template["family"]), []).append(template)
        fields = template["form"]["fields"]
        assert {str(field["name"]) for field in fields} == set(template["args"])
        assert all(isinstance(field.get("label"), str) and field["label"].strip() for field in fields)
        assert all(
            isinstance(field.get("description"), str) and field["description"].strip() and field.get("description_source") in {"declared", "generated"}
            for field in fields
        )
        assert all(
            template["args"][str(field["name"])]["description"] == field["description"]
            and template["args"][str(field["name"])]["description_source"] == field["description_source"]
            for field in fields
        )

    assert len(visible_families) == 51
    assert len(templates) == 54
    assert set(templates_by_family) == visible_families

    achievement = next(template for template in templates if template["id"] == "pihc3:achievement/basic")
    achievement_fields = {str(field["name"]): field for field in achievement["form"]["fields"]}
    assert achievement_fields["unique_id"]["label"] == "Unique ID"

    autonomous_state = next(template for template in templates if template["id"] == "pihc3:autonomous_state/basic")
    autonomous_state_fields = {str(field["name"]): field for field in autonomous_state["form"]["fields"]}
    assert autonomous_state_fields["ai_subject_wants_higher_factor"]["label"] == "AI subject wants higher factor"

    for family in sorted(visible_families):
        slots = registry.source_slots_for(family)
        assert slots
        assert all(slot.kind == "loc" for slot in slots if slot.name == "loc")
        assert all(slot.authoring_path for slot in slots if slot.kind == "copy")

        family_view = registry.to_view(family=family)["families"][0]
        required_loc_keys = family_view.get("localization", {}).get(
            "required_keys",
            [],
        )
        if required_loc_keys:
            assert all(any(str(path).endswith((".loc", ".yml")) for path in template["files"]) for template in templates_by_family[family])


def test_pihc3_numeric_template_fields_explain_units_to_people_and_agents() -> None:
    templates = Project.load(PIHC3_ROOT).templates(
        authoring_ready=True,
        source="project",
    )["templates"]
    numeric_fields = [
        (str(template["id"]), str(name), spec) for template in templates for name, spec in template["args"].items() if spec.get("type") == "number"
    ]

    assert len(numeric_fields) == 24
    assert not [(template_id, name) for template_id, name, spec in numeric_fields if not spec.get("label") or not spec.get("description")]
    fields = {(template_id, name): spec for template_id, name, spec in numeric_fields}
    assert fields[("pihc3:idea/basic", "cic")]["description"] == ("Decimal factory-output modifier; use 0.02 for 2%.")
    assert fields[("pihc3:military_industrial_organization/basic", "reliability")]["description"] == "Decimal equipment bonus; use 0.05 for 5%."
    assert "70-day" in fields[("pihc3:focus/basic", "cost")]["description"]
    assert "150%" in fields[("pihc3:technology/basic", "research_cost")]["description"]
    assert fields[("pihc3:decision/basic", "cost")]["description"] == ("Political-power cost paid when the decision is taken.")
    assert fields[("pihc3:equipment/basic", "year")]["description"] == ("Model year recorded in the equipment definition.")
    assert fields[("pihc3:doctrine/subdoctrine-basic", "diagram_x")]["description"] == ("Hidden tree-layout X owned by this doctrine.")
    assert fields[("pihc3:doctrine/subdoctrine-basic", "diagram_y")]["description"] == ("Hidden tree-layout Y owned by this doctrine.")


def test_pihc3_high_traffic_families_own_complete_domain_help() -> None:
    templates = Project.load(PIHC3_ROOT).templates(
        authoring_ready=True,
        source="project",
    )["templates"]
    high_traffic_families = {
        "character",
        "country",
        "decision",
        "equipment",
        "event",
        "focus",
        "idea",
        "technology",
    }
    selected = [template for template in templates if template["family"] in high_traffic_families]
    fields = [field for template in selected for field in template["form"]["fields"]]

    assert len(selected) == 10
    assert len(fields) == 61
    assert all(field["description_source"] == "declared" for field in fields)

    by_template = {str(template["id"]): {str(field["name"]): field for field in template["form"]["fields"]} for template in selected}
    assert by_template["pihc3:character/basic"]["gender"]["choices"] == [
        "female",
        "male",
        "undefined",
    ]
    assert by_template["pihc3:decision/basic"]["cost"]["type"] == "number"
    assert by_template["pihc3:equipment/basic"]["year"]["type"] == "number"
    assert by_template["pihc3:equipment/basic"]["active"]["choices"] == [
        "yes",
        "no",
    ]
    assert by_template["pihc3:technology/basic"]["dependencies"]["advanced"] is True


def test_pihc3_texticon_and_ui_extensions_own_guided_pdx_and_image_slots() -> None:
    project = Project.load(PIHC3_ROOT)
    registry = project._build_registry(profile=project.game)
    expected = {
        "texticon": {
            "path": SOURCE_ROOT / "modules/texticon/PIHC_TEXTICONS - PIHC TEXTICONS/interface/PIHC_texticons.gfx",
            "slots": {
                ("definitions", "pdx", None),
                ("images", "copy", "gfx/texticons/{filename}"),
            },
            "control_id": "pdx-control-002",
            "replacement": True,
        },
        "ui": {
            "path": SOURCE_ROOT / "modules/ui/alerts - alerts/interface/alerts.gui",
            "slots": {
                ("layout", "pdx", None),
                ("alert_images", "copy", "gfx/interface/alerts/{filename}"),
                (
                    "autonomy_images",
                    "copy",
                    "gfx/interface/autonomy/{filename}",
                ),
            },
            "control_id": "pdx-control-003",
            "replacement": 1,
        },
    }

    for family_id, contract in expected.items():
        slots = registry.source_slots_for(family_id)
        assert {(slot.name, slot.kind, slot.authoring_path) for slot in slots} == contract["slots"]

        source_path = contract["path"]
        source_text = source_path.read_text(encoding="utf-8")
        form = project.source_form(source_path)

        assert form is not None
        assert form["family"] == family_id
        assert form["source_format"] == "pdx"
        assert form["contract"] == "paradev.pdx.guided-form.v1"

        plan = project.plan_source_form_update(
            source_path,
            {contract["control_id"]: contract["replacement"]},
        )

        assert plan["schema"] == "paradev.source-form-update.v1"
        assert plan["source_format"] == "pdx"
        assert plan["changed"] is True
        assert plan["changes"][0]["control_id"] == contract["control_id"]
        assert plan["source_edit"]["expected_size"] == len(source_text.encode("utf-8"))
        assert source_path.read_text(encoding="utf-8") == source_text


def test_pihc3_map_entities_declare_guided_province_and_victory_point_lists() -> None:
    project = Project.load(PIHC3_ROOT)
    cases = {
        "state": {
            "path": SOURCE_ROOT / "modules/state/199 - 马鞍岛东岸/def.txt",
            "lists": {
                "provinces": {
                    "columns": 1,
                    "minimum": 1,
                    "value_prefix": "345\n1637\n3122",
                },
                "victory_points": {
                    "columns": 2,
                    "minimum": 0,
                    "value_prefix": "345 5",
                },
            },
        },
        "strategic_region": {
            "path": SOURCE_ROOT / "modules/strategic_region/106 - 谷望角/def.txt",
            "lists": {
                "provinces": {
                    "columns": 1,
                    "minimum": 1,
                    "value_prefix": "503\n739\n770",
                },
            },
        },
    }

    for family_id, case in cases.items():
        source_path = case["path"]
        source_text = source_path.read_text(encoding="utf-8")
        form = project.source_form(source_path)
        assert form is not None
        assert form["family"] == family_id
        controls = [
            control for section in form["sections"] for control in section["controls"] if control.get("patch", {}).get("op") == "replace-pdx-integer-list"
        ]
        by_key = {control["patch"]["path"][-1]["key"]: control for control in controls}
        assert set(by_key) == set(case["lists"])
        for key, expected in case["lists"].items():
            control = by_key[key]
            assert control["control"] == "text"
            assert control["multiline"] is True
            assert control["value"].startswith(expected["value_prefix"])
            assert control["patch"]["columns"] == expected["columns"]
            assert control["patch"]["minimum"] == expected["minimum"]

        first = by_key["provinces"]
        replacement = first["value"] + "\n20000"
        plan = project.plan_source_form_update(
            source_path,
            {first["id"]: replacement},
        )
        assert plan["changed"] is True
        assert plan["source_format"] == "pdx"
        assert source_path.read_text(encoding="utf-8") == source_text


def test_pihc3_script_containers_declare_guided_block_body_authoring() -> None:
    project = Project.load(PIHC3_ROOT)
    registry = project._build_registry(profile=project.game)
    cases = {
        "scripted_effect": {
            "path": SOURCE_ROOT / "modules/scripted_effect/ADD_FOG_OF_WAR_BUILDING - ADD FOG OF WAR BUILDING/def.txt",
            "keys": {"ADD_FOG_OF_WAR_BUILDING"},
            "template_args": {"body"},
        },
        "scripted_trigger": {
            "path": SOURCE_ROOT / "modules/scripted_trigger/is_pony_country - is pony country/def.txt",
            "keys": {"is_pony_country"},
            "template_args": {"body"},
        },
        "on_action": {
            "path": SOURCE_ROOT / "modules/on_action/EVENT_TIMELINE_15_on_actions - EVENT TIMELINE 15 on actions/def.txt",
            "keys": {"on_actions"},
            "template_args": {"effect_body"},
        },
        "scripted_gui": {
            "path": SOURCE_ROOT
            / (
                "modules/scripted_gui/"
                "pihc_inventory_item_4EP_C08_PIN_GAME_2_CODEBOOK_buttons - "
                "pihc inventory item 4EP C08 PIN GAME 2 CODEBOOK buttons/def.txt"
            ),
            "keys": {"visible", "triggers", "effects"},
            "template_args": {"effects_body", "triggers_body", "properties_body"},
        },
    }
    templates = {
        str(template["family"]): template
        for template in project.templates(authoring_ready=True, source="project")["templates"]
        if str(template["family"]) in cases
    }
    scaffold_values = {
        "scripted_effect": {
            "title": "ParaDev dry effect",
            "body": "add_political_power = 10",
        },
        "scripted_trigger": {
            "title": "ParaDev dry trigger",
            "body": "always = yes",
        },
        "on_action": {
            "title": "ParaDev dry on-action",
            "hook": "on_monthly",
            "effect_body": "add_political_power = 10",
        },
        "scripted_gui": {
            "title": "ParaDev dry scripted GUI",
            "effects_body": "dry_click = { add_political_power = 1 }",
            "triggers_body": "dry_visible = { always = yes }",
            "properties_body": "",
        },
    }

    for family_id, case in cases.items():
        family = registry.family(family_id)
        hints = getattr(family, "source_form_field_hints", None)
        assert isinstance(hints, dict)
        assert all(hint.get("control") == "block-text" for hint in hints.values())
        source_path = case["path"]
        source_text = source_path.read_text(encoding="utf-8")
        form = project.source_form(source_path)
        assert form is not None
        controls: list[dict[str, object]] = []
        stack = list(form["sections"])
        while stack:
            section = stack.pop()
            controls.extend(section.get("controls", []))
            stack.extend(section.get("sections", []))
        body_controls = [control for control in controls if control.get("patch", {}).get("op") == "replace-pdx-block-body"]
        keys = {control["patch"]["path"][-1]["key"] for control in body_controls}
        assert case["keys"] <= keys
        assert all(control.get("multiline") is True for control in body_controls)
        first = body_controls[0]
        replacement = str(first["value"]) + "\n# ParaDev guided block-body dry run"
        plan = project.plan_source_form_update(source_path, {first["id"]: replacement})
        assert plan["changed"] is True
        assert plan["source_format"] == "pdx"
        assert source_path.read_text(encoding="utf-8") == source_text
        assert case["template_args"] <= set(templates[family_id]["args"])
        scaffold = project.scaffold_module(
            str(templates[family_id]["id"]),
            f"PARADEV_DRY_{family_id.upper()}",
            values=scaffold_values[family_id],
            write=False,
        )
        assert scaffold["blocked"] is False
        assert scaffold["written"] is False
        assert len(scaffold["files"]) == 1


def test_pihc3_equipment_module_categories_use_registry_localization_and_image_editors() -> None:
    project = Project.load(PIHC3_ROOT)
    registry = project._build_registry(profile=project.game)
    slots = registry.source_slots_for("equipment_module_category")

    assert {slot.kind for slot in slots} == {"copy", "loc"}
    assert not [slot for slot in slots if slot.kind == "pdx"]

    source_path = SOURCE_ROOT / ("modules/equipment_module_category/" "pihc_plane_armor_type_2_magic - 魔能装甲/main.loc")
    form = project.source_form(source_path)
    assert form is not None
    assert form["source_format"] == "loc"
    assert form["contract"] == "paradev.localization.text-form.v1"
    assert form["coverage"] == {
        "truncated": False,
        "shown_controls": 2,
        "total_controls": 2,
    }
    controls = [control for section in form["sections"] for control in section["controls"]]
    assert [control["value"] for control in controls] == [
        "Arcane Magic Armor",
        "魔能装甲",
    ]
    assert all(control["patch"]["op"] == "replace-loc-text" for control in controls)


def test_every_pihc3_module_localization_source_has_a_bounded_lossless_form() -> None:
    paths = tuple(sorted((SOURCE_ROOT / "modules").rglob("*.loc")))
    partial = 0
    for path in paths:
        relative = path.relative_to(SOURCE_ROOT / "modules")
        family, folder = relative.parts[:2]
        object_id = folder.split(" - ", 1)[0]
        form = loc_text_source_form(
            module_id=f"{family}/{object_id}",
            text=path.read_text(encoding="utf-8"),
        )
        assert form is not None, relative
        assert form["contract"] == "paradev.localization.text-form.v1"
        coverage = form["coverage"]
        assert coverage["shown_controls"] > 0
        assert coverage["shown_controls"] <= coverage["total_controls"]
        partial += int(coverage["truncated"])

    assert len(paths) == 5_159
    assert partial == 40


def test_pihc3_entity_extension_projects_every_portable_record_into_bounded_forms() -> None:
    project = Project.load(PIHC3_ROOT)
    family = project._build_registry(profile=project.game).family("entity")
    record_paths = tuple(sorted((SOURCE_ROOT / "modules/entity").glob("*/record.json")))
    control_counts: list[int] = []

    assert len(record_paths) == 134
    for path in record_paths:
        object_id = path.parent.name.split(" - ", 1)[0]
        form = family.source_form(
            module_id=f"entity/{object_id}",
            relative_path="record.json",
            text=path.read_text(encoding="utf-8"),
        )

        assert isinstance(form, dict), path
        assert form["contract"] == "pihc2.entity.record.v1"
        sections = form["sections"]
        assert isinstance(sections, list)
        assert 1 <= len(sections) <= 64
        controls = [control for section in sections for control in section["controls"]]
        assert controls
        assert len(controls) <= 192
        assert all(control["patch"]["op"] == "replace-json-scalar" and control["patch"]["path"] for control in controls)
        control_counts.append(len(controls))

    assert min(control_counts) == 13
    assert max(control_counts) == 184


def test_pihc3_entity_source_form_is_registry_owned_lossless_and_fail_closed() -> None:
    project = Project.load(PIHC3_ROOT)
    family = project._build_registry(profile=project.game).family("entity")
    source_path = SOURCE_ROOT / "modules/entity/VIENTO_MIRROR - Viento Mirror/record.json"
    source_text = source_path.read_text(encoding="utf-8")

    payload = project.source_form(source_path)

    assert payload is not None
    assert payload["schema"] == "paradev.source-form.v1"
    assert payload["family"] == "entity"
    assert payload["module_id"] == "entity/VIENTO_MIRROR"
    assert payload["source_format"] == "json"
    assert payload["contract"] == "pihc2.entity.record.v1"
    controls = [control for section in payload["sections"] for control in section["controls"]]
    by_path = {tuple(control["patch"]["path"]): control for control in controls}
    assert len(controls) == 13
    assert by_path[("mesh", "scale")]["value"] == 4.0
    assert by_path[("entities", 0, "state", "looping")]["value"] is True
    assert by_path[("entities", 0, "state", "event", "particle")]["value"] == "mirror_particle"
    assert source_path.read_text(encoding="utf-8") == source_text

    dense_record = {
        "mesh": {"scale": 1},
        "entities": [
            {
                "name": f"ENTITY_{index}",
                "pdxmesh": f"MESH_{index}",
                "scale": 1,
                "default_state": "idle",
            }
            for index in range(49)
        ],
    }
    assert (
        family.source_form(
            module_id="entity/TOO_COMPLEX",
            relative_path="record.json",
            text=json.dumps(dense_record),
        )
        is None
    )
    assert (
        family.source_form(
            module_id="entity/VIENTO_MIRROR",
            relative_path=".paradev/entities.json",
            text=source_text,
        )
        is None
    )

    duplicate_path = SOURCE_ROOT / "modules/entity/VIENTO_AIR_AIRSHIP - Viento Air Airship/record.json"
    duplicate_form = family.source_form(
        module_id="entity/VIENTO_AIR_AIRSHIP",
        relative_path="record.json",
        text=duplicate_path.read_text(encoding="utf-8"),
    )
    duplicate_sections = {section["label"]: section for section in duplicate_form["sections"]}
    second_event = duplicate_sections["Entities › Item 1 › State › Event (2)"]
    assert second_event["controls"][0]["patch"]["path"] == [
        "entities",
        0,
        "state",
        "event__D1",
        "time",
    ]
    sound_section = duplicate_sections["Entities › Item 1 › State › Event (2) › Sound"]
    assert sound_section["controls"][0]["label"] == "Sound effect"


def test_pihc3_entity_record_form_is_available_through_the_authoring_mcp() -> None:
    from paradev.surfaces.mcp import create_authoring_mcp_toolkit

    payload = create_authoring_mcp_toolkit().run(
        "module_source_form",
        path=str(PIHC3_ROOT),
        module_id="entity/VIENTO_MIRROR",
        relative_path="record.json",
    )

    assert payload["schema"] == "paradev.mcp.module-source-form.v1"
    assert payload["module_id"] == "entity/VIENTO_MIRROR"
    assert payload["supported"] is True
    assert payload["source"]["size"] == len(payload["source"]["text"].encode("utf-8"))
    assert payload["source"]["mtime_ns"].isdigit()
    assert payload["form"]["source_format"] == "json"
    assert payload["form"]["contract"] == "pihc2.entity.record.v1"

    update = create_authoring_mcp_toolkit().run(
        "module_source_form_update",
        path=str(PIHC3_ROOT),
        module_id="entity/VIENTO_MIRROR",
        relative_path="record.json",
        values={"entity-record-control-000": 4.5},
    )
    assert update["schema"] == "paradev.source-form-update.v1"
    assert update["module_id"] == "entity/VIENTO_MIRROR"
    assert update["changed"] is True
    assert update["changes"][0]["control_id"] == "entity-record-control-000"
    assert update["source_edit"]["expected_size"] == payload["source"]["size"]
    assert update["source_edit"]["expected_mtime_ns"] == payload["source"]["mtime_ns"]


def test_pihc3_entity_record_guided_update_plan_is_no_write_and_revision_guarded() -> None:
    from heavenbase.utils import loads_json

    project = Project.load(PIHC3_ROOT)
    source_path = SOURCE_ROOT / "modules/entity/VIENTO_MIRROR - Viento Mirror/record.json"
    source_text = source_path.read_text(encoding="utf-8")

    plan = project.plan_source_form_update(
        source_path,
        {"entity-record-control-000": 4.5},
    )

    assert plan["schema"] == "paradev.source-form-update.v1"
    assert plan["module_id"] == "entity/VIENTO_MIRROR"
    assert plan["form_contract"] == "pihc2.entity.record.v1"
    assert plan["changes"] == [
        {
            "control_id": "entity-record-control-000",
            "previous": 4.0,
            "value": 4.5,
        }
    ]
    assert loads_json(plan["source_edit"]["text"], restore=False)["mesh"]["scale"] == 4.5
    assert plan["source_edit"]["expected_size"] == len(source_text.encode("utf-8"))
    assert str(plan["source_edit"]["expected_mtime_ns"]).isdigit()
    assert source_path.read_text(encoding="utf-8") == source_text


def test_pihc3_entity_records_support_one_no_write_guided_mcp_batch() -> None:
    from paradev.surfaces.mcp import create_authoring_mcp_toolkit

    mirror_path = SOURCE_ROOT / "modules/entity/VIENTO_MIRROR - Viento Mirror/record.json"
    airship_path = SOURCE_ROOT / ("modules/entity/VIENTO_AIR_AIRSHIP - Viento Air Airship/record.json")
    before = {
        mirror_path: mirror_path.read_text(encoding="utf-8"),
        airship_path: airship_path.read_text(encoding="utf-8"),
    }

    plan = create_authoring_mcp_toolkit().run(
        "module_source_form_update_batch",
        path=str(PIHC3_ROOT),
        updates=[
            {
                "module_id": "entity/VIENTO_MIRROR",
                "relative_path": "record.json",
                "values": {"entity-record-control-000": 4.5},
            },
            {
                "module_id": "entity/VIENTO_AIR_AIRSHIP",
                "relative_path": "record.json",
                "values": {"entity-record-control-000": 3.5},
            },
        ],
    )

    assert plan["schema"] == "paradev.source-form-update-batch.v1"
    assert plan["project_id"] == "PIHC3"
    assert plan["changed"] is True
    assert plan["counts"] == {
        "requested": 2,
        "changed": 2,
        "unchanged": 0,
    }
    assert [row["module_id"] for row in plan["updates"]] == [
        "entity/VIENTO_MIRROR",
        "entity/VIENTO_AIR_AIRSHIP",
    ]
    assert [edit["path"] for edit in plan["source_edits"]] == [
        str(mirror_path),
        str(airship_path),
    ]
    assert all(str(edit["expected_mtime_ns"]).isdigit() for edit in plan["source_edits"])
    assert {path: path.read_text(encoding="utf-8") for path in before} == before


def test_diagram_surfaces_have_no_central_family_dispatch_table() -> None:
    repository = Path(__file__).resolve().parents[1]
    sdk_source = (repository / "src/paradev/sdk/project.py").read_text(encoding="utf-8")
    desktop_source = (repository / "apps/desktop/src/projectModules.ts").read_text(encoding="utf-8")

    for retired_helper in (
        "_doctrine_diagram_sources",
        "_focus_tree_diagram_images",
        "_focus_tree_diagram_localization",
        "_mio_diagram_enrichment",
        "_mio_diagram_sources",
        "_modular_focus_tree_edit_plan",
        "_modular_focus_tree_projection",
        "_modular_focus_tree_sources",
    ):
        assert retired_helper not in sdk_source
    assert "PROJECT_DIAGRAM_FAMILY_CAPABILITY_BY_ID" not in desktop_source
    assert "diagram_views_by_family" in (repository / "src/paradev/build/registry.py").read_text(encoding="utf-8")


def test_pihc3_custom_entities_are_self_contained_heavenbase_extensions() -> None:
    extension_roots = {path.name: path for path in (PIHC3_ROOT / "extensions").iterdir() if path.is_dir() and not path.name.startswith(".")}

    for family_id in (
        "entity",
        "equipment",
        "equipment_module",
        "inventory_item",
        "state_lore",
    ):
        root = extension_roots[family_id]
        source = (root / "__init__.py").read_text(encoding="utf-8")
        descriptor = load_yaml(
            str(_extension_descriptor(root)),
            strict=True,
        )

        assert "hb.Entity" in source
        assert "resource_slots" in source
        assert "compilation_hooks" in source
        assert "build_family" in source
        assert isinstance(descriptor, dict)
        items = descriptor.get("items")
        assert isinstance(items, list)
        assert any(isinstance(row, dict) and row.get("kind") == "paradev_build_family" for row in items)


def test_pihc3_project_entities_are_reserved_for_project_owned_schemas() -> None:
    entity_count = 0
    extension_roots = (path for path in (PIHC3_ROOT / "extensions").iterdir() if path.is_dir() and not path.name.startswith("."))
    for root in sorted(extension_roots):
        descriptor = load_yaml(
            str(_extension_descriptor(root)),
            strict=True,
        )
        assert isinstance(descriptor, dict)
        items = descriptor.get("items")
        assert isinstance(items, list)
        entities = [row for row in items if isinstance(row, dict) and row.get("kind") == "entity"]
        if root.name in BUILTIN_COMPILER_OVERLAYS:
            assert not entities
            assert not [row for row in items if isinstance(row, dict) and row.get("kind") == "extension"]
            source = (root / "__init__.py").read_text(encoding="utf-8")
            assert "hb.Entity" not in source
            assert "import heavenbase" not in source
            continue
        if not entities:
            assert root.name == "localisation"
            continue
        assert len(entities) == 1
        entity = entities[0]
        assert entity["source"] == "path"
        target = entity.get("target")
        assert isinstance(target, dict)
        assert target.get("module") is None
        assert isinstance(target.get("qualname"), str)

        source = (root / "__init__.py").read_text(encoding="utf-8")
        assert "hb.Entity" in source
        assert "resource_slots" in source
        assert "compilation_hooks" in source
        entity_count += 1

    assert entity_count == 63


def test_every_pihc3_template_uses_titled_folders_and_minimal_metadata() -> None:
    template_count = 0
    descriptor_paths = sorted(path / ".paradev/meta.yaml" for path in (PIHC3_ROOT / "extensions").iterdir() if path.is_dir() and not path.name.startswith("."))
    for descriptor_path in descriptor_paths:
        descriptor = load_yaml(str(descriptor_path), strict=True)
        assert isinstance(descriptor, dict)
        items = descriptor.get("items")
        assert isinstance(items, list)
        for item in items:
            if not isinstance(item, dict):
                continue
            if item.get("kind") != "paradev_authoring_template":
                continue
            declaration = item["meta"]["definition"]["declaration"]
            assert declaration["directory"] == "{object_id} - {title}"

            files = declaration["files"]
            visible_metadata = files.get("meta.yaml")
            if declaration["family"] == "decision":
                assert visible_metadata is None
            if visible_metadata is not None:
                assert visible_metadata.startswith(("collection:", "comment:"))
                assert "title:" not in visible_metadata
                assert "settings:" not in visible_metadata

            system_files = declaration.get("system_files", {})
            assert set(system_files) <= {
                ".paradev/diagram.yaml",
                ".paradev/meta.yaml",
            }
            if ".paradev/diagram.yaml" in system_files:
                assert declaration["family"] == "doctrine"
                diagram_source = system_files[".paradev/diagram.yaml"]
                assert "paradev.hoi4.doctrine-diagram-state.v1" in diagram_source
            if declaration["family"] == "focus" and declaration.get("kind", "module") == "module":
                assert system_files[".paradev/meta.yaml"].startswith("collection:")
            template_count += 1

    assert template_count == 54


def test_pihc3_extension_owns_doctrine_diagram_initialization() -> None:
    sdk_path = Path(__file__).resolve().parents[1] / "src/paradev/sdk/project.py"
    sdk_source = sdk_path.read_text(encoding="utf-8")
    doctrine_descriptor = load_yaml(
        str(_extension_descriptor(PIHC3_ROOT / "extensions/doctrine")),
        strict=True,
    )
    templates = [item for item in doctrine_descriptor["items"] if item.get("kind") == "paradev_authoring_template"]

    assert "_module_system_scaffold_files" not in sdk_source
    assert len(templates) == 2
    assert all(set(item["meta"]["definition"]["declaration"]["system_files"]) == {".paradev/diagram.yaml"} for item in templates)
