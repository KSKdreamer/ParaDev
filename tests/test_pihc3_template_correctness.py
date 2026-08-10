from __future__ import annotations

import os
from dataclasses import replace

import pytest
from heavenbase.utils import (
    copy_dir,
    exists_file,
    get_file_basename,
    load_txt,
    load_yaml,
    loads_json,
    pj,
)

from paradev.games.hoi4 import MIOTraitSource, mio_trait_diagram_projection
from paradev.sdk import Project

pytestmark = [pytest.mark.integration, pytest.mark.slow]

PIHC3_ROOT = pj(os.environ.get("PARADEV_PIHC3_ROOT", "projects/PIHC3"), abs=True)
PREFERRED_LANGUAGE = "zh"
PREFERRED_LANGUAGE_FOLDER = "simp_chinese"
PREFERRED_LANGUAGE_KEY = "l_simp_chinese"


def test_pihc3_relational_template_fields_declare_existing_collection_hints() -> None:
    templates = Project.load(PIHC3_ROOT).templates()
    rows = {str(row["id"]): row for row in templates["templates"]}

    assert rows["pihc3:focus/basic"]["args"]["tree"]["reference"] == {
        "kind": "collection",
        "family": "focus",
    }
    assert rows["pihc3:decision/basic"]["args"]["category_id"]["reference"] == {
        "kind": "collection",
        "family": "decision",
    }


@pytest.fixture
def isolated_pihc3_template_project(tmp_path) -> Project:
    """Return PIHC3's real template contracts with an isolated source tree."""

    source = Project.load(PIHC3_ROOT)
    root = tmp_path.resolve()
    copy_dir(source.root / "extensions", root / "extensions")
    return replace(
        source,
        root=root,
        manifest_path=root / "paradev.yaml",
        source_roots=(root / "src",),
        output_root=root / "build/mod",
        build_root=root / ".paradev/.cache/build",
        extension_modules=tuple(root / "extensions" / path.name for path in source.extension_modules),
        python_modules=(),
        copy_roots=(),
    )


def test_every_pihc3_template_scaffolds_and_passes_its_entity_contract(
    isolated_pihc3_template_project: Project,
) -> None:
    """Keep every visible PIHC3 creation path buildable from an empty project."""

    project = isolated_pihc3_template_project
    templates = [row for row in project.templates(authoring_ready=True)["templates"] if str(row["id"]).startswith("pihc3:")]
    collection_templates = [row for row in templates if row["kind"] == "collection"]
    module_templates = [row for row in templates if row["kind"] == "module"]
    families = {str(row["family"]) for row in templates}

    assert len(templates) == 54
    assert len(module_templates) == 52
    assert len(collection_templates) == 2
    assert len(families) == 51
    assert not [f"{row['id']}:{path}" for row in templates for path in row.get("files", ()) if str(path).casefold() in {"meta.yaml", "meta.yml"}]

    tree_id = "TEMPLATE_MATRIX_FOCUS_TREE"
    collection_inputs = {
        "pihc3:decision-category/basic": (
            "DECISION_CATEGORY_TEMPLATE_MATRIX",
            {"title": "Template Matrix Decision Category"},
        ),
        "pihc3:focus-tree/basic": (
            tree_id,
            {
                "title": "Template Matrix Focus Tree",
                "country_tag": "P99",
            },
        ),
    }
    assert {str(row["id"]) for row in collection_templates} == set(collection_inputs)
    for template in collection_templates:
        template_id = str(template["id"])
        collection_id, values = collection_inputs[template_id]
        review = project.scaffold_collection(
            template_id,
            collection_id,
            values=values,
        )
        apply = project.scaffold_collection(
            template_id,
            collection_id,
            values=values,
            write=True,
            plan_hash=str(review["plan_hash"]),
        )
        assert review["blocked"] is False
        assert apply["blocked"] is False
        assert apply["written"] is True
        assert not exists_file(pj(apply["root"], "meta.yaml"))

    object_ids = {
        "country": "P99",
        "state": "9901",
        "state_lore": "STATE_LORE_9901",
        "strategic_region": "9902",
    }
    failures: list[str] = []
    built_families: set[str] = set()
    expected_asset_errors = {
        "entity.missing_animation_asset",
        "entity.missing_mesh_asset",
    }

    template_indexes: dict[str, int] = {}
    for template in module_templates:
        template_id = str(template["id"])
        family = str(template["family"])
        template_index = template_indexes.get(family, 0)
        template_indexes[family] = template_index + 1
        base_object_id = object_ids.get(
            family,
            f"TEMPLATE_MATRIX_{family.upper()}",
        )
        object_id = base_object_id if template_index == 0 else f"{base_object_id}_{template_index + 1}"
        values: dict[str, object] = {
            "title": f"Template Matrix {family.replace('_', ' ').title()}",
        }
        if family == "focus":
            values["tree"] = tree_id
        try:
            plan = project.create_module(
                template_id,
                object_id,
                values=values,
            )
        except Exception as exc:  # noqa: BLE001  # pragma: no cover - matrix detail
            failures.append(f"{template_id}: scaffold raised {exc!r}")
            continue
        if plan["blocked"] or not plan["written"]:
            failures.append(f"{template_id}: scaffold blocked: {plan['diagnostics']!r}")
            continue
        if exists_file(pj(plan["root"], "meta.yaml")) or exists_file(pj(plan["root"], "meta.yml")):
            failures.append(f"{template_id}: scaffold created visible metadata")
            continue

        result = project.build(
            module_id=f"{family}/{object_id}",
            strict_metadata=True,
            emit_artifacts=True,
        )
        errors = {diagnostic.code for diagnostic in result.diagnostics if diagnostic.severity == "error"}
        if family == "entity":
            if errors != expected_asset_errors:
                failures.append(f"{template_id}: expected explicit 3D asset requirements, " f"got {sorted(errors)!r}")
            continue
        if result.blocked or errors:
            failures.append(f"{template_id}: strict build failed: {sorted(errors)!r}")
            continue
        built_families.add(family)

    assert not failures, "\n".join(failures)
    assert built_families == families - {"entity"}


def test_pihc3_portrait_template_starts_from_authored_source_without_metadata(
    isolated_pihc3_template_project: Project,
) -> None:
    object_id = "PORTRAIT_TEMPLATE_CONTRACT"
    plan = isolated_pihc3_template_project.create_module(
        "pihc3:portrait/basic",
        object_id,
        values={"title": "Template Contract Portrait"},
    )

    result = isolated_pihc3_template_project.build(
        module_id=f"portrait/{object_id}",
        strict_metadata=True,
        emit_artifacts=True,
    )
    root = plan["root"]
    definition_path = pj(root, "portraits", f"{object_id}.txt")
    definition = load_txt(definition_path, encoding="utf-8")
    errors = [diagnostic for diagnostic in result.diagnostics if diagnostic.severity == "error"]

    assert plan["blocked"] is False
    assert plan["written"] is True
    assert not exists_file(pj(root, "meta.yaml"))
    assert definition == (f"{object_id} = {{\n" "    male = {}\n" "    female = {}\n" "}\n")
    assert result.blocked is False
    assert not errors
    assert f"portraits/{object_id}.txt" in {artifact.path for artifact in result.artifacts}


def test_pihc3_decision_template_infers_category_without_metadata(
    isolated_pihc3_template_project: Project,
) -> None:
    object_id = "DECISION_TEMPLATE_CONTRACT"
    category_id = "DECISION_CATEGORY_TEMPLATE_CONTRACT"
    plan = isolated_pihc3_template_project.create_module(
        "pihc3:decision/basic",
        object_id,
        values={
            "title": "Template Contract Decision",
            "category_id": category_id,
        },
    )

    result = isolated_pihc3_template_project.build(
        module_id=f"decision/{object_id}",
        strict_metadata=True,
        emit_artifacts=True,
    )

    assert plan["blocked"] is False
    assert plan["written"] is True
    assert not exists_file(pj(plan["root"], "meta.yaml"))
    assert result.blocked is False
    assert not [diagnostic for diagnostic in result.diagnostics if diagnostic.severity == "error"]
    assert next(module for module in result.modules if module.module_id == f"decision/{object_id}").collection_id == category_id
    assert f"common/decisions/{category_id}.txt" in {artifact.path for artifact in result.artifacts}


def test_pihc3_decision_inference_rejects_ambiguous_definition(
    isolated_pihc3_template_project: Project,
) -> None:
    object_id = "DECISION_AMBIGUOUS_CONTRACT"
    plan = isolated_pihc3_template_project.create_module(
        "pihc3:decision/basic",
        object_id,
        values={"title": "Ambiguous Decision"},
    )
    definition = pj(plan["root"], "def.txt")
    with open(definition, "w", encoding="utf-8") as stream:
        stream.write("DECISION_CATEGORY_ONE = { DECISION_AMBIGUOUS_CONTRACT = {} }\n" "DECISION_CATEGORY_TWO = { DECISION_AMBIGUOUS_CONTRACT_2 = {} }\n")

    result = isolated_pihc3_template_project.build(
        module_id=f"decision/{object_id}",
        strict_metadata=True,
    )

    assert result.blocked is True
    diagnostic = next(diagnostic for diagnostic in result.diagnostics if diagnostic.code == "decision.ambiguous_category")
    assert diagnostic.module_id == f"decision/{object_id}"
    assert diagnostic.source_path == "def.txt"


def test_pihc3_country_template_passes_strict_targeted_build(
    isolated_pihc3_template_project: Project,
) -> None:
    object_id = "COUNTRY_TEMPLATE_CONTRACT"
    plan = isolated_pihc3_template_project.create_module(
        "pihc3:country/basic",
        object_id,
        values={"title": "Template Contract Country"},
    )

    result = isolated_pihc3_template_project.build(
        module_id=f"country/{object_id}",
        strict_metadata=True,
        emit_artifacts=True,
    )
    artifact_paths = {artifact.path for artifact in result.artifacts}
    localization = load_txt(pj(plan["root"], "main.loc"), encoding="utf-8")
    country_output = isolated_pihc3_template_project.output_root / f"common/countries/{object_id}.txt"

    assert plan["blocked"] is False
    assert plan["written"] is True
    assert not exists_file(pj(plan["root"], "meta.yaml"))
    assert result.blocked is False
    assert result.dry_run is False
    assert not [diagnostic for diagnostic in result.diagnostics if diagnostic.severity == "error"]
    assert f"common/countries/{object_id}.txt" in artifact_paths
    assert f"localisation/{PREFERRED_LANGUAGE_FOLDER}/" f"{object_id}_{PREFERRED_LANGUAGE_KEY}.yml" in artifact_paths
    assert country_output.is_file()
    assert "graphical_culture = western_european_gfx" in load_txt(country_output, encoding="utf-8")
    assert f"[{PREFERRED_LANGUAGE}.{object_id}_DESC]" in localization
    assert f"[{PREFERRED_LANGUAGE}.{object_id}_desc]" not in localization


def test_pihc3_state_lore_template_derives_and_builds_numeric_state_id(
    isolated_pihc3_template_project: Project,
) -> None:
    object_id = "STATE_LORE_217"
    template_view = isolated_pihc3_template_project.templates(
        template_id="pihc3:state_lore/basic",
    )
    template = template_view["templates"][0]
    state_id_arg = template["args"]["state_id"]
    plan = isolated_pihc3_template_project.create_module(
        "pihc3:state_lore/basic",
        object_id,
        values={"title": "Template Contract Lore"},
    )
    override_plan = isolated_pihc3_template_project.create_module(
        "pihc3:state_lore/basic",
        "STATE_LORE_CUSTOM",
        values={"title": "Custom State Contract Lore", "state_id": 218},
        write=False,
    )
    invalid_plan = isolated_pihc3_template_project.create_module(
        "pihc3:state_lore/basic",
        "STATE_LORE_NOT_NUMERIC",
        values={"title": "Invalid State Contract Lore"},
        write=False,
    )

    result = isolated_pihc3_template_project.build(
        module_id=f"state_lore/{object_id}",
        strict_metadata=True,
        emit_artifacts=True,
    )
    artifact_paths = {artifact.path for artifact in result.artifacts}
    on_actions_output = isolated_pihc3_template_project.output_root / "common/on_actions/PIHC_STATE_LORES.txt"

    assert state_id_arg["required"] is False
    assert state_id_arg["type"] == "number"
    assert state_id_arg["default"] == "{family_tag}"
    assert state_id_arg["advanced"] is True
    assert plan["blocked"] is False
    assert plan["written"] is True
    assert plan["values"]["state_id"] == "217"
    assert [get_file_basename(str(file["path"])) for file in plan["files"]] == ["main.loc"]
    assert override_plan["blocked"] is False
    assert override_plan["values"]["state_id"] == "218"
    assert invalid_plan["blocked"] is True
    assert invalid_plan["written"] is False
    assert any(diagnostic["code"] == "scaffold.invalid_number" for diagnostic in invalid_plan["diagnostics"])
    assert not exists_file(pj(plan["root"], "meta.yaml"))
    assert not exists_file(pj(plan["root"], ".paradev", "meta.yaml"))
    assert result.blocked is False
    assert result.dry_run is False
    assert not [diagnostic for diagnostic in result.diagnostics if diagnostic.severity == "error"]
    assert "common/scripted_localisation/PIHC_STATE_LORES.txt" in artifact_paths
    assert "common/on_actions/PIHC_STATE_LORES.txt" in artifact_paths
    assert f"localisation/{PREFERRED_LANGUAGE_FOLDER}/" f"{object_id}_{PREFERRED_LANGUAGE_KEY}.yml" in artifact_paths
    assert on_actions_output.is_file()
    assert "global.states_with_lore = 217.id" in load_txt(on_actions_output, encoding="utf-8")


def test_pihc3_grand_doctrine_template_emits_doctrine_definition(
    isolated_pihc3_template_project: Project,
) -> None:
    object_id = "DOCTRINE_TEMPLATE_CONTRACT"
    plan = isolated_pihc3_template_project.create_module(
        "pihc3:doctrine/grand-basic",
        object_id,
        values={"title": "Template Contract Doctrine"},
    )

    result = isolated_pihc3_template_project.build(
        module_id=f"doctrine/{object_id}",
        strict_metadata=True,
        emit_artifacts=True,
    )
    artifact_paths = {artifact.path for artifact in result.artifacts}
    diagram_state = load_yaml(
        pj(plan["root"], ".paradev", "diagram.yaml"),
        encoding="utf-8",
        strict=True,
    )
    diagram = isolated_pihc3_template_project.module_diagram("doctrine")
    doctrine_output = isolated_pihc3_template_project.output_root / f"common/doctrines/grand_doctrines/{object_id}.txt"

    assert plan["blocked"] is False
    assert plan["written"] is True
    assert not exists_file(pj(plan["root"], "meta.yaml"))
    assert not exists_file(pj(plan["root"], ".paradev", "meta.yaml"))
    assert diagram_state == {
        "schema": "paradev.hoi4.doctrine-diagram-state.v1",
        "position": {"x": 0, "y": 0},
        "paths": [],
        "mutually_exclusive": [],
    }
    assert diagram["editable"] is True
    assert diagram["diagnostics"] == []
    assert len(diagram["nodes"]) == 1
    assert diagram["nodes"][0]["id"] == object_id
    assert diagram["nodes"][0]["module_id"] == f"doctrine/{object_id}"
    assert diagram["nodes"][0]["compiled_id"] == object_id
    assert diagram["nodes"][0]["editable"] is True
    assert diagram["nodes"][0]["x"] == 0
    assert diagram["nodes"][0]["y"] == 0
    assert diagram["nodes"][0]["source_path"].endswith("/def.txt")
    assert diagram["nodes"][0]["diagram_source_path"].endswith("/.paradev/diagram.yaml")
    assert diagram["nodes"][0]["source_revision"].startswith("sha256:")
    assert result.blocked is False
    assert result.dry_run is False
    assert not [diagnostic for diagnostic in result.diagnostics if diagnostic.severity == "error"]
    assert f"common/doctrines/grand_doctrines/{object_id}.txt" in artifact_paths
    assert f"localisation/{PREFERRED_LANGUAGE_FOLDER}/" f"{object_id}_{PREFERRED_LANGUAGE_KEY}.yml" in artifact_paths
    assert doctrine_output.is_file()
    doctrine_text = load_txt(doctrine_output, encoding="utf-8")
    assert f"{object_id} = {{" in doctrine_text
    assert "tracks = {" in doctrine_text
    assert "planning_speed = 0.05" in doctrine_text


def test_pihc3_technology_template_keeps_selected_parent_in_one_scaffold(
    isolated_pihc3_template_project: Project,
) -> None:
    parent_id = "TECHNOLOGY_TEMPLATE_PARENT"
    child_id = "TECHNOLOGY_TEMPLATE_CHILD"
    isolated_pihc3_template_project.create_module(
        "pihc3:technology/basic",
        parent_id,
        values={
            "title": "Template Parent",
            "folder": "industry_folder",
            "x": 4,
            "y": 7,
        },
    )
    plan = isolated_pihc3_template_project.create_module(
        "pihc3:technology/basic",
        child_id,
        values={
            "title": "Template Child",
            "folder": "industry_folder",
            "x": 4,
            "y": 9,
            "dependencies": (f"dependencies = {{\n\t\t\t{parent_id} = 1\n\t\t}}"),
        },
    )

    definition = load_txt(pj(plan["root"], "def.txt"), encoding="utf-8")
    diagram = isolated_pihc3_template_project.module_diagram("technology")
    result = isolated_pihc3_template_project.build(family="technology")

    assert plan["blocked"] is False
    assert "\t\t\tname = industry_folder" in definition
    assert "\t\t\t\tx = 4" in definition
    assert "\t\t\t\ty = 9" in definition
    assert f"\t\t\t{parent_id} = 1" in definition
    assert {(edge["kind"], edge["source"], edge["target"]) for edge in diagram["edges"]} >= {("dependency", parent_id, child_id)}
    assert result.blocked is False


def test_pihc3_doctrine_template_keeps_selected_layout_and_path_in_one_scaffold(
    isolated_pihc3_template_project: Project,
) -> None:
    parent_id = "DOCTRINE_TEMPLATE_PARENT"
    child_id = "DOCTRINE_TEMPLATE_CHILD"
    isolated_pihc3_template_project.create_module(
        "pihc3:doctrine/grand-basic",
        parent_id,
        values={"title": "Template Parent"},
    )
    plan = isolated_pihc3_template_project.create_module(
        "pihc3:doctrine/grand-basic",
        child_id,
        values={
            "title": "Template Child",
            "diagram_x": 3,
            "diagram_y": 5,
            "diagram_paths": f"\n  - {parent_id}",
        },
    )

    state = load_yaml(
        pj(plan["root"], ".paradev", "diagram.yaml"),
        encoding="utf-8",
        strict=True,
    )
    diagram = isolated_pihc3_template_project.module_diagram("doctrine")
    result = isolated_pihc3_template_project.build(family="doctrine")

    assert plan["blocked"] is False
    assert state["position"] == {"x": 3, "y": 5}
    assert state["paths"] == [parent_id]
    assert {(edge["kind"], edge["source"], edge["target"]) for edge in diagram["edges"]} >= {("path", child_id, parent_id)}
    assert result.blocked is False


def test_pihc3_mio_template_keeps_selected_trait_position_in_one_scaffold(
    isolated_pihc3_template_project: Project,
) -> None:
    object_id = "MIO_TEMPLATE_POSITION"
    plan = isolated_pihc3_template_project.create_module(
        "pihc3:military_industrial_organization/basic",
        object_id,
        values={
            "title": "Template Position MIO",
            "x": 6,
            "y": 8,
        },
    )

    source_path = pj(
        plan["root"],
        "common",
        "military_industrial_organization",
        "organizations",
        f"{object_id}.txt",
    )
    definition = load_txt(source_path, encoding="utf-8")
    diagram = isolated_pihc3_template_project.module_diagram("military_industrial_organization")
    result = isolated_pihc3_template_project.build(family="military_industrial_organization")

    assert plan["blocked"] is False
    assert "      x = 6" in definition
    assert "      y = 8" in definition
    quality = next(node for node in diagram["nodes"] if node.get("trait_id") == f"{object_id}_quality")
    assert (quality["x"], quality["y"]) == (6, 8)
    assert result.blocked is False


def test_pihc3_doctrine_batch_creation_initializes_hidden_tree_state(
    isolated_pihc3_template_project: Project,
) -> None:
    isolated_pihc3_template_project.source_roots[0].mkdir(
        parents=True,
        exist_ok=True,
    )
    requests = [
        {
            "template_id": "pihc3:doctrine/grand-basic",
            "object_id": object_id,
            "values": {"title": title},
        }
        for object_id, title in (
            ("DOCTRINE_BATCH_ALPHA", "Batch Alpha"),
            ("DOCTRINE_BATCH_BETA", "Batch Beta"),
        )
    ]

    plan = isolated_pihc3_template_project.create_modules(requests)
    applied = isolated_pihc3_template_project.create_modules(
        requests,
        write=True,
        plan_hash=plan["plan_hash"],
    )
    diagram = isolated_pihc3_template_project.module_diagram("doctrine")

    assert plan["blocked"] is False
    assert all(any(file.get("system") is True and file["module_path"] == ".paradev/diagram.yaml" for file in row["files"]) for row in plan["modules"])
    assert applied["blocked"] is False
    assert applied["counts"]["created"] == 2
    assert diagram["editable"] is True
    assert diagram["diagnostics"] == []
    assert {node["id"] for node in diagram["nodes"]} == {
        "DOCTRINE_BATCH_ALPHA",
        "DOCTRINE_BATCH_BETA",
    }
    assert all(node["editable"] is True for node in diagram["nodes"])


def test_pihc3_mio_template_builds_one_exact_tree_editable_organization(
    isolated_pihc3_template_project: Project,
) -> None:
    object_id = "MIO_TEMPLATE_CONTRACT"
    plan = isolated_pihc3_template_project.create_module(
        "military_industrial_organization",
        object_id,
        values={
            "title": "Template Contract Arsenal",
            "description": "A minimal tree-editable PIHC3 organization.",
            "country_tag": "C01",
            "reliability": 0.08,
        },
    )

    result = isolated_pihc3_template_project.build(
        module_id=f"military_industrial_organization/{object_id}",
        strict_metadata=True,
        emit_artifacts=True,
    )
    root = plan["root"]
    definition_path = pj(
        root,
        "common",
        "military_industrial_organization",
        "organizations",
        f"{object_id}.txt",
    )
    definition = load_txt(definition_path, encoding="utf-8")
    source_path = "/".join(
        (
            "src/modules/military_industrial_organization",
            object_id,
            "common/military_industrial_organization",
            "organizations",
            f"{object_id}.txt",
        )
    )
    projection_source = MIOTraitSource(source_path, definition)
    projection = mio_trait_diagram_projection([projection_source])
    artifact_paths = {artifact.path for artifact in result.artifacts}
    definition_output = "/".join(
        (
            "common/military_industrial_organization",
            "organizations",
            f"{object_id}.txt",
        )
    )
    localization_output = "/".join(
        (
            "localisation",
            PREFERRED_LANGUAGE_FOLDER,
            (f"MILITARY_INDUSTRIAL_ORGANIZATION_{object_id}_" f"{PREFERRED_LANGUAGE_KEY}.yml"),
        )
    )
    errors = [diagnostic for diagnostic in result.diagnostics if diagnostic.severity == "error"]

    assert plan["blocked"] is False
    assert plan["written"] is True
    assert not exists_file(pj(root, "meta.yaml"))
    assert result.blocked is False
    assert result.dry_run is False
    assert not errors
    assert definition_output in artifact_paths
    assert localization_output in artifact_paths
    assert "reliability = 0.08" in definition
    assert projection["editable"] is True
    assert projection["diagnostics"] == []
    assert projection["summary"]["organization_count"] == 1
    assert projection["summary"]["trait_count"] == 2
    assert projection["summary"]["initial_trait_count"] == 1
    assert projection["summary"]["positioned_trait_count"] == 1


def test_pihc3_inventory_template_builds_effects_and_triggers(
    isolated_pihc3_template_project: Project,
) -> None:
    object_id = "TEMPLATE_CONTRACT_RELIC"
    template_view = isolated_pihc3_template_project.templates(
        template_id="pihc3:inventory_item/basic",
    )
    template = template_view["templates"][0]
    plan = isolated_pihc3_template_project.create_module(
        "pihc3:inventory_item/basic",
        object_id,
        values={
            "title": "Template Contract Relic",
            "description": ("A complete inventory item created from one folder identity."),
            "count": 2,
        },
    )

    result = isolated_pihc3_template_project.build(
        module_id=f"inventory_item/{object_id}",
        strict_metadata=True,
        emit_artifacts=True,
    )
    root = plan["root"]
    item = loads_json(load_txt(pj(root, "item.json"), encoding="utf-8"))
    localization = load_txt(pj(root, "main.loc"), encoding="utf-8")
    artifact_paths = {artifact.path for artifact in result.artifacts}
    effects_output = "/".join(
        (
            "common/scripted_effects",
            f"PIHC_INVENTORY_ITEM_{object_id}.txt",
        )
    )
    triggers_output = "/".join(
        (
            "common/scripted_triggers",
            f"PIHC_INVENTORY_ITEM_{object_id}.txt",
        )
    )
    errors = [diagnostic for diagnostic in result.diagnostics if diagnostic.severity == "error"]
    effects_artifact = next(artifact for artifact in result.artifacts if artifact.path == effects_output)
    triggers_artifact = next(artifact for artifact in result.artifacts if artifact.path == triggers_output)
    effects = effects_artifact.payload.to_str()
    triggers = triggers_artifact.payload.to_str()

    assert "item_tag" not in template["args"]
    assert template["args"]["count"]["type"] == "number"
    assert template["args"]["count"]["default"] == "1"
    assert not exists_file(pj(root, "def.txt"))
    assert not exists_file(pj(root, "meta.yaml"))
    assert not exists_file(pj(root, "effects.txt"))
    assert not exists_file(pj(root, "triggers.txt"))
    assert item == {"helper_quantities": "2"}
    assert result.blocked is False
    assert result.dry_run is False
    assert not errors
    assert f"ADD_INVENTORY_ITEM_{object_id}_2" in effects
    assert f"VAR_INVENTORY_ITEM_{object_id} = 2" in effects
    assert f"TRIGGER_HAVE_INVENTORY_ITEM_{object_id}" in triggers
    assert f"TRIGGER_HAVE_INVENTORY_ITEM_{object_id}_2" in triggers
    assert f"[{PREFERRED_LANGUAGE}.INVENTORY_ITEM_{object_id}]" in localization
    assert f"CUSTOM_GAIN_INVENTORY_ITEM_{object_id}_2" not in localization
    assert effects_output in artifact_paths
    assert triggers_output in artifact_paths


def test_pihc3_equipment_module_template_builds_minimal_aggregate_module(
    isolated_pihc3_template_project: Project,
) -> None:
    object_id = "MODULE_TEMPLATE_CONTRACT"
    template_view = isolated_pihc3_template_project.templates(
        template_id="pihc3:equipment_module/basic",
    )
    template = template_view["templates"][0]
    plan = isolated_pihc3_template_project.create_module(
        "pihc3:equipment_module/basic",
        object_id,
        values={
            "title": "Template Contract Equipment Module",
            "description": "A module created without importer metadata.",
        },
    )

    browser = isolated_pihc3_template_project.browser(
        kind="module",
        module_id=f"equipment_module/{object_id}",
    )
    result = isolated_pihc3_template_project.build(
        module_id=f"equipment_module/{object_id}",
        strict_metadata=True,
        emit_artifacts=True,
    )
    root = plan["root"]
    definition = load_txt(pj(root, "def.txt"), encoding="utf-8")
    aggregate_path = isolated_pihc3_template_project.output_root / "common" / "units" / "equipment" / "modules" / "00_plane_modules.txt"
    artifact_paths = {artifact.path for artifact in result.artifacts}
    [browser_item] = browser["items"]
    expected_relative_path = "src/modules/equipment_module/" "MODULE_TEMPLATE_CONTRACT - Template Contract Equipment Module/icon.png"
    errors = [diagnostic for diagnostic in result.diagnostics if diagnostic.severity == "error"]
    aggregate_output = "common/units/equipment/modules/00_plane_modules.txt"

    assert template["directory"] == "{object_id} - {title}"
    assert "module_type" not in template["args"]
    assert template["args"]["stat_value"]["type"] == "number"
    assert template["args"]["xp_cost"]["type"] == "number"
    assert plan["blocked"] is False
    assert plan["written"] is True
    assert not exists_file(pj(root, "meta.yaml"))
    assert not exists_file(pj(root, ".paradev", "meta.yaml"))
    assert f"{object_id} = {{" in definition
    assert "category = pihc_plane_special_type_0" in definition
    assert "build_cost_ic = 0" in definition
    assert browser_item["image_targets"] == [
        {
            "slot": "icon",
            "slot_kinds": ["copy"],
            "name": "icon.png",
            "path": pj(root, "icon.png"),
            "relative_path": expected_relative_path,
            "extension": "png",
            "exists": False,
        }
    ]
    assert result.blocked is False
    assert result.dry_run is False
    assert not errors
    assert aggregate_output in artifact_paths
    assert f"localisation/{PREFERRED_LANGUAGE_FOLDER}/" f"{object_id}_{PREFERRED_LANGUAGE_KEY}.yml" in artifact_paths
    assert aggregate_path.is_file()
    assert f"{object_id} = {{" in load_txt(aggregate_path, encoding="utf-8")
