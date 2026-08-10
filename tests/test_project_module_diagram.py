from __future__ import annotations

import os
from pathlib import Path

import pytest
from heavenbase.utils import dumps_yaml

from paradev.build import BuildResult, Diagnostic
from paradev.games.hoi4 import MIO_TRAIT_DIAGRAM_PROJECTION_SCHEMA
from paradev.games.hoi4.doctrine import (
    DOCTRINE_DIAGRAM_PROJECTION_SCHEMA,
    DOCTRINE_DIAGRAM_STATE_SCHEMA,
)
from paradev.games.hoi4.focus_tree import (
    FOCUS_TREE_DIAGRAM_PROJECTION_SCHEMA,
    FOCUS_TREE_NODE_CREATION_PLAN_SCHEMA,
)
from paradev.sdk import Project
from paradev.sdk._module_diagram_api import (
    MAX_MODULE_DIAGRAM_EDGE_INTENTS,
)


def _technology_source(
    technology_id: str,
    *,
    x: int,
    y: int,
    dependency: str | None = None,
    path_target: str | None = None,
) -> str:
    dependency_text = "        dependencies = {\n" f"            {dependency} = 1\n" "        }\n" if dependency else ""
    path_text = "        path = {\n" f"            leads_to_tech = {path_target}\n" "            research_cost_coeff = 1\n" "        }\n" if path_target else ""
    return (
        "technologies = {\n"
        f"    {technology_id} = {{\n"
        "        folder = {\n"
        "            name = infantry_folder\n"
        "            position = {\n"
        f"                x = {x}\n"
        f"                y = {y}\n"
        "            }\n"
        "        }\n"
        f"{dependency_text}"
        f"{path_text}"
        "        research_cost = 1\n"
        "    }\n"
        "}\n"
    )


def _write_technology_project(root: Path) -> Project:
    (root / "paradev.yaml").write_text(
        "\n".join(
            (
                "project_id: technology_diagram",
                "title: Technology Diagram",
                "game: hoi4",
                "source_roots: [src]",
                "output_root: build/mod",
                "build_root: .paradev/.cache/build",
                "families:",
                "  technology:",
                "    source_slots:",
                "      - {name: def, match: def.txt, kind: pdx, required: true}",
                "    templates:",
                "      pdx: common/technologies/{object_id}.txt",
            )
        )
        + "\n",
        encoding="utf-8",
    )
    alpha = root / "src/modules/technology/TECH_ALPHA - Alpha"
    beta = root / "src/modules/technology/TECH_BETA - Beta"
    alpha.mkdir(parents=True)
    beta.mkdir(parents=True)
    (alpha / "def.txt").write_text(
        _technology_source(
            "TECH_ALPHA",
            x=1,
            y=2,
            path_target="TECH_BETA",
        ),
        encoding="utf-8",
    )
    (beta / "def.txt").write_text(
        _technology_source(
            "TECH_BETA",
            x=2,
            y=3,
            dependency="TECH_ALPHA",
        ),
        encoding="utf-8",
    )
    (beta / "meta.yaml").write_text("title: Beta\n", encoding="utf-8")
    return Project.load(root)


def _focus_tree_source() -> str:
    return (
        "focus_tree = {\n"
        "    id = TEST_TREE\n"
        "    focus = {\n"
        "        id = FOCUS_A\n"
        "        icon = GFX_FOCUS_A_icon\n"
        "        x = 0\n"
        "        y = 0\n"
        "    }\n"
        "    focus = {\n"
        "        id = FOCUS_B\n"
        "        icon = GFX_FOCUS_B_icon\n"
        "        prerequisite = {\n"
        "            focus = FOCUS_A\n"
        "        }\n"
        "        x = 1\n"
        "        y = 1\n"
        "    }\n"
        "    focus = {\n"
        "        id = FOCUS_C\n"
        "        icon = GFX_FOCUS_C_icon\n"
        "        x = 2\n"
        "        y = 2\n"
        "    }\n"
        "    focus = {\n"
        '        id = "FOCUS_DON\'T"\n'
        "        x = 3\n"
        "        y = 3\n"
        "    }\n"
        "}\n"
    )


def _write_focus_tree_project(root: Path) -> Project:
    (root / "paradev.yaml").write_text(
        "\n".join(
            (
                "project_id: focus_tree_diagram",
                "title: Focus Tree Diagram",
                "game: hoi4",
                "source_roots: [src]",
                "output_root: build/mod",
                "build_root: .paradev/.cache/build",
                "families:",
                "  focus_tree:",
                "    source_slots:",
                "      - {name: def, match: def.txt, kind: pdx, required: true}",
                "      - {name: loc, match: '**/*.loc', kind: loc, many: true}",
                "    templates:",
                "      pdx: common/national_focus/{object_id}.txt",
                "      loc: localisation/{language_folder}/{object_id}_{language}.yml",
            )
        )
        + "\n",
        encoding="utf-8",
    )
    tree = root / "src/modules/focus_tree/TEST_TREE"
    tree.mkdir(parents=True)
    (tree / "def.txt").write_text(
        _focus_tree_source(),
        encoding="utf-8",
    )
    (tree / "meta.yaml").write_text(
        "\n".join(
            (
                "title: This metadata title must not name embedded focuses",
                "settings:",
                "  focuses:",
                "    - id: FOCUS_B",
                "      localized_titles:",
                "        l_english: Metadata fallback is forbidden",
            )
        )
        + "\n",
        encoding="utf-8",
    )
    (tree / "main.loc").write_text(
        "\n".join(
            (
                "[l_english.FOCUS_A]",
                "Authored Alpha",
                "",
                "[l_simp_chinese.FOCUS_A]",
                "源始阿尔法",
                "",
                "[l_english.FOCUS_A_desc]",
                "Authored Alpha description",
                "",
                "[l_english.FOCUS_B]",
                "Authored Beta",
                "",
                "[l_english.FOCUS_DON_T]",
                "Authored apostrophe focus",
                "",
                "[l_english.FOCUS_DON_T_desc]",
                "Authored apostrophe description",
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return Project.load(root)


def _write_mio_project(root: Path) -> Project:
    fixture_root = Path(__file__).parent / "fixtures" / "hoi4_mio"
    (root / "paradev.yaml").write_text(
        "\n".join(
            (
                "project_id: mio_diagram",
                "title: MIO Diagram",
                "game: hoi4",
                "source_roots: [src]",
                "output_root: build/mod",
                "build_root: .paradev/.cache/build",
                "families:",
                "  military_industrial_organization:",
                "    source_slots:",
                "      - {name: pdx, match: def.txt, kind: pdx, required: true, many: true}",
                "      - {name: loc, match: '**/*.loc', kind: loc, many: true}",
                "    templates:",
                "      pdx: common/military_industrial_organization/organizations/{object_id}.txt",
                "      loc: localisation/{language_folder}/{object_id}_{language}.yml",
            )
        )
        + "\n",
        encoding="utf-8",
    )
    family_root = root / "src/modules/military_industrial_organization"
    organizations = family_root / "MIO_ORGANIZATIONS"
    debug = family_root / "MIO_DEBUG"
    organizations.mkdir(parents=True)
    debug.mkdir(parents=True)
    (organizations / "def.txt").write_text(
        (fixture_root / "organizations.txt").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    localization = (fixture_root / "main.loc").read_text(encoding="utf-8")
    cross_module_entry = "[l_english.standardized_alloys_trait]\n" "Standardized Alloys\n\n"
    (organizations / "main.loc").write_text(
        localization.replace(cross_module_entry, ""),
        encoding="utf-8",
    )
    (debug / "def.txt").write_text(
        (fixture_root / "debug_organizations.txt").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (debug / "cross_module.loc").write_text(
        cross_module_entry,
        encoding="utf-8",
    )
    return Project.load(root)


def _write_doctrine_project(root: Path) -> Project:
    (root / "paradev.yaml").write_text(
        "\n".join(
            (
                "project_id: doctrine_diagram",
                "title: Doctrine Diagram",
                "game: hoi4",
                "source_roots: [src]",
                "output_root: build/mod",
                "build_root: .paradev/.cache/build",
                "families:",
                "  doctrine:",
                "    source_slots:",
                "      - {name: def, match: def.txt, kind: pdx, required: true}",
                "      - {name: loc, match: '**/*.loc', kind: loc, many: true}",
                "      - {name: icon, match: icon.png}",
                "    templates:",
                "      pdx: common/doctrines/grand_doctrines/{object_id}.txt",
                "      loc: localisation/{language_folder}/{object_id}_{language}.yml",
            )
        )
        + "\n",
        encoding="utf-8",
    )
    for doctrine_id, compiled_id, title, x, y, paths, exclusions in (
        (
            "DOCTRINE_ROOT",
            "compiled_root",
            "Root Doctrine",
            0,
            0,
            ("DOCTRINE_LEFT",),
            ("DOCTRINE_RIGHT",),
        ),
        (
            "DOCTRINE_LEFT",
            "compiled_left",
            "Left Doctrine",
            -2,
            2,
            (),
            (),
        ),
        (
            "DOCTRINE_RIGHT",
            "compiled_right",
            "Right Doctrine",
            2,
            2,
            (),
            ("DOCTRINE_ROOT",),
        ),
    ):
        module_root = root / "src/modules/doctrine" / doctrine_id
        system_root = module_root / ".paradev"
        system_root.mkdir(parents=True)
        (module_root / "meta.yaml").write_text(
            f"title: {title}\n",
            encoding="utf-8",
        )
        (module_root / "def.txt").write_text(
            f"{compiled_id} = {{\n\txp_cost = 100\n}}\n",
            encoding="utf-8",
        )
        (system_root / "diagram.yaml").write_text(
            dumps_yaml(
                {
                    "schema": DOCTRINE_DIAGRAM_STATE_SCHEMA,
                    "position": {"x": x, "y": y},
                    "paths": list(paths),
                    "mutually_exclusive": list(exclusions),
                },
                sort_keys=False,
            ),
            encoding="utf-8",
        )
    return Project.load(root)


def test_project_browser_discovers_registered_diagram_capabilities(
    tmp_path: Path,
) -> None:
    project = _write_technology_project(tmp_path)

    summary = project.browser_summary()
    full = project.browser()

    for payload in (summary, full):
        technology = next(row for row in payload["families"] if row["family"] == "technology")
        assert technology["diagram"] == {
            "id": "technology",
            "aliases": ["technologies"],
            "renderer": "technology",
            "title": "Technology tree",
            "editable": True,
            "authoring_kind": "module",
            "selection_defaults": [
                {"field": "folder", "source": "folder"},
                {"field": "x", "source": "x"},
                {"field": "y", "source": "y", "offset": 2},
                {
                    "field": "dependencies",
                    "source": "id",
                    "template": ("dependencies = {\n" "\t\t\t{value} = 1\n" "\t\t}"),
                },
            ],
            "relationships": [
                {
                    "kind": "dependency",
                    "label": "Prerequisite",
                    "visual_kind": "dependency",
                    "selected_endpoint": "target",
                    "owner_endpoint": "target",
                    "symmetric": False,
                    "cardinality": "many",
                },
                {
                    "kind": "path",
                    "label": "Unlock path",
                    "visual_kind": "path",
                    "selected_endpoint": "source",
                    "owner_endpoint": "source",
                    "symmetric": False,
                    "cardinality": "many",
                },
            ],
        }


def test_project_doctrine_diagram_edits_hidden_state_and_builds(
    tmp_path: Path,
) -> None:
    project = _write_doctrine_project(tmp_path)
    left_root = tmp_path / "src/modules/doctrine/DOCTRINE_LEFT"
    state_path = left_root / ".paradev/diagram.yaml"
    definition_path = left_root / "def.txt"
    metadata_path = left_root / "meta.yaml"
    before_definition = definition_path.read_bytes()
    before_metadata = metadata_path.read_bytes()

    projection = project.module_diagram("doctrines")

    assert projection == project.module_diagram("doctrine")
    assert projection["schema"] == "paradev.sdk.module_diagram.v1"
    assert projection["provider_schema"] == DOCTRINE_DIAGRAM_PROJECTION_SCHEMA
    assert projection["family"] == "doctrine"
    assert projection["editable"] is True
    nodes = {str(row["id"]): row for row in projection["nodes"]}
    assert nodes["DOCTRINE_LEFT"]["compiled_id"] == "compiled_left"
    assert (
        nodes["DOCTRINE_LEFT"]["x"],
        nodes["DOCTRINE_LEFT"]["y"],
    ) == (-2, 2)
    assert {(row["kind"], row["source"], row["target"]) for row in projection["edges"]} == {
        ("path", "DOCTRINE_ROOT", "DOCTRINE_LEFT"),
        ("mutually_exclusive", "DOCTRINE_RIGHT", "DOCTRINE_ROOT"),
    }

    intents = [
        {
            "doctrine_id": "DOCTRINE_LEFT",
            "x": -4,
            "y": 3,
            "source_revision": nodes["DOCTRINE_LEFT"]["source_revision"],
        }
    ]
    plan = project.edit_module_diagram(
        "doctrine",
        position_intents=intents,
    )

    assert plan["status"] == "planned"
    assert plan["blocked"] is False
    assert [row["path"] for row in plan["drafts"]] == ["src/modules/doctrine/DOCTRINE_LEFT/.paradev/diagram.yaml"]
    assert definition_path.read_bytes() == before_definition
    assert metadata_path.read_bytes() == before_metadata

    applied = project.edit_module_diagram(
        "doctrines",
        position_intents=intents,
        write=True,
        plan_hash=str(plan["plan_hash"]),
    )

    assert applied["status"] == "applied"
    assert applied["written"] is True
    assert applied["validation"]["family"] == "doctrine"
    assert "    x: -4\n    y: 3\n" in state_path.read_text(encoding="utf-8")
    assert definition_path.read_bytes() == before_definition
    assert metadata_path.read_bytes() == before_metadata

    result = project.build(family="doctrine", emit_artifacts=True)

    assert result.blocked is False
    assert (project.output_root / "common/doctrines/grand_doctrines/DOCTRINE_LEFT.txt").is_file()


def test_project_mio_diagram_reads_exact_sources_and_applies_guarded_edits(
    tmp_path: Path,
) -> None:
    project = _write_mio_project(tmp_path)
    source_path = tmp_path / "src/modules/military_industrial_organization" / "MIO_ORGANIZATIONS/def.txt"

    projection = project.module_diagram("mio")

    assert projection == project.module_diagram("military_industrial_organization")
    with pytest.raises(ValueError, match="has no registered source provider"):
        project.module_diagram("military_industrial_organization_component")
    assert projection["schema"] == "paradev.sdk.module_diagram.v1"
    assert projection["provider_schema"] == MIO_TRAIT_DIAGRAM_PROJECTION_SCHEMA
    assert projection["family"] == "military_industrial_organization"
    assert projection["source_kind"] == "module_pdx_source"
    assert projection["editable"] is True
    assert projection["summary"]["organization_count"] == 4
    assert projection["summary"]["trait_count"] == 7
    assert len(projection["nodes"]) == 7
    assert not any(row["code"] == "module_diagram.no_nodes" for row in projection["diagnostics"])
    assert all(str(row["module_id"]).startswith("military_industrial_organization/") for row in projection["nodes"])
    standardized = next(row for row in projection["nodes"] if row.get("trait_id") == "standardized_alloys_trait")
    assert standardized["localized_titles"] == {
        "l_english": "Standardized Alloys",
    }
    assert standardized["module_id"] == ("military_industrial_organization/MIO_ORGANIZATIONS")
    organization = next(row for row in projection["organizations"] if row["organization_id"] == "C01_Imperial_Royal_Airship_Manufacturing organization")
    assert organization["localized_titles"] == {
        "l_english": "Royal Airship Manufacturer",
        "l_simp_chinese": "皇家飞船制造商",
    }
    assert projection["sources"] == sorted(
        projection["sources"],
        key=lambda row: row["path"],
    )

    intent = {
        "organization_id": standardized["organization_id"],
        "trait_id": standardized["trait_id"],
        "x": 4,
        "y": -2,
        "source_revision": standardized["source_revision"],
    }
    plan = project.edit_module_diagram(
        "mio",
        position_intents=[intent],
    )

    assert plan["provider_schema"] == ("paradev.hoi4.mio-trait-diagram-plan.v1")
    assert plan["family"] == "military_industrial_organization"
    assert plan["status"] == "planned"
    assert plan["blocked"] is False
    assert [row["path"] for row in plan["drafts"]] == ["src/modules/military_industrial_organization/" "MIO_ORGANIZATIONS/def.txt"]

    applied = project.edit_module_diagram(
        "military_industrial_organization",
        position_intents=[intent],
        write=True,
        plan_hash=str(plan["plan_hash"]),
    )

    assert applied["status"] == "applied"
    assert applied["written"] is True
    assert applied["validation"]["family"] == ("military_industrial_organization")
    assert "x = 4" in source_path.read_text(encoding="utf-8")
    assert "y = -2" in source_path.read_text(encoding="utf-8")


def test_project_mio_diagram_creates_trait_through_registered_node_plan(
    tmp_path: Path,
) -> None:
    project = _write_mio_project(tmp_path)
    projection = project.module_diagram("mio")
    parent = next(row for row in projection["nodes"] if row.get("trait_id") == "standardized_alloys_trait")
    node_intent = {
        "organization_id": parent["organization_id"],
        "parent_trait_id": parent["trait_id"],
        "trait_id": "precision_tools_trait",
        "title": "Precision Tools",
        "icon": "GFX_generic_mio_trait_icon_reliability",
        "x": parent["x"],
        "y": parent["y"] + 1,
        "bonus_key": "reliability",
        "bonus_value": 0.05,
        "language": "en",
        "source_path": parent["source_path"],
        "source_revision": parent["source_revision"],
    }

    plan = project.edit_module_diagram(
        "mio",
        node_intents=[node_intent],
    )

    assert plan["status"] == "planned"
    assert plan["blocked"] is False
    assert len(plan["drafts"]) == 2
    assert {row["path"].rsplit("/", 1)[-1] for row in plan["drafts"]} == {"def.txt", "main.loc"}
    with pytest.raises(ValueError, match="cannot be combined"):
        project.edit_module_diagram(
            "mio",
            position_intents=[
                {
                    "organization_id": parent["organization_id"],
                    "trait_id": parent["trait_id"],
                    "x": parent["x"],
                    "y": parent["y"],
                    "source_revision": parent["source_revision"],
                }
            ],
            node_intents=[node_intent],
        )

    applied = project.edit_module_diagram(
        "mio",
        node_intents=[node_intent],
        write=True,
        plan_hash=str(plan["plan_hash"]),
    )
    refreshed = project.module_diagram("mio")

    assert applied["status"] == "applied"
    assert applied["written"] is True
    assert applied["validation"]["family"] == ("military_industrial_organization")
    created = next(row for row in refreshed["nodes"] if row.get("trait_id") == "precision_tools_trait")
    assert created["localized_titles"] == {
        "l_english": "Precision Tools",
    }
    assert created["position"] == {
        "x": parent["x"],
        "y": parent["y"] + 1,
    }
    assert {
        (row["kind"], row["source_trait_id"], row["target_trait_id"]) for row in refreshed["edges"] if row["target_trait_id"] == "precision_tools_trait"
    } == {
        (
            "any_parent",
            "standardized_alloys_trait",
            "precision_tools_trait",
        ),
        (
            "relative_position",
            "standardized_alloys_trait",
            "precision_tools_trait",
        ),
    }


def test_project_technology_diagram_edits_authoritative_source_and_builds(
    tmp_path: Path,
) -> None:
    project = _write_technology_project(tmp_path)
    beta_path = tmp_path / "src/modules/technology/TECH_BETA - Beta/def.txt"
    meta_path = beta_path.with_name("meta.yaml")
    before_meta = meta_path.read_bytes()

    projection = project.module_diagram("technologies")

    assert projection["schema"] == "paradev.sdk.module_diagram.v1"
    assert projection["family"] == "technology"
    assert projection["editable"] is True
    nodes = {str(row["id"]): row for row in projection["nodes"] if isinstance(row, dict)}
    assert (nodes["TECH_BETA"]["x"], nodes["TECH_BETA"]["y"]) == (2, 3)
    assert {(row["kind"], row["source"], row["target"]) for row in projection["edges"]} == {
        ("dependency", "TECH_ALPHA", "TECH_BETA"),
        ("path", "TECH_ALPHA", "TECH_BETA"),
    }

    position_intents = [
        {
            "technology_id": "TECH_BETA",
            "x": 9,
            "y": 4,
            "source_revision": nodes["TECH_BETA"]["source_revision"],
        }
    ]
    edge_intents = [
        {
            "kind": "dependency",
            "source_id": "TECH_ALPHA",
            "target_id": "TECH_BETA",
            "present": False,
            "source_revision": nodes["TECH_BETA"]["source_revision"],
        }
    ]
    plan = project.edit_module_diagram(
        "technology",
        position_intents=position_intents,
        edge_intents=edge_intents,
    )

    assert plan["schema"] == "paradev.sdk.module_diagram_edit.v1"
    assert plan["status"] == "planned"
    assert plan["blocked"] is False
    assert plan["written"] is False
    assert [row["path"] for row in plan["drafts"]] == ["src/modules/technology/TECH_BETA - Beta/def.txt"]
    assert meta_path.read_bytes() == before_meta

    applied = project.edit_module_diagram(
        "technology",
        position_intents=position_intents,
        edge_intents=edge_intents,
        write=True,
        plan_hash=str(plan["plan_hash"]),
    )

    assert applied["status"] == "applied"
    assert applied["blocked"] is False
    assert applied["applied"] is True
    assert applied["written"] is True
    assert applied["validation"]["family"] == "technology"
    assert applied["validation"]["blocked"] is False
    assert meta_path.read_bytes() == before_meta
    text = beta_path.read_text(encoding="utf-8")
    assert "x = 9" in text
    assert "y = 4" in text
    assert "TECH_ALPHA = 1" not in text
    assert (tmp_path / "src/modules/technology/TECH_ALPHA - Alpha/def.txt").read_text(encoding="utf-8").count("leads_to_tech = TECH_BETA") == 1

    result = project.build(family="technology", emit_artifacts=True)

    assert result.blocked is False
    emitted = project.output_root / "common/technologies/TECH_BETA.txt"
    assert emitted.is_file()
    assert "x = 9" in emitted.read_text(encoding="utf-8")


def test_project_focus_tree_diagram_edits_authoritative_source_and_builds(
    tmp_path: Path,
) -> None:
    project = _write_focus_tree_project(tmp_path)
    source_path = tmp_path / "src/modules/focus_tree/TEST_TREE/def.txt"
    meta_path = source_path.with_name("meta.yaml")
    before_meta = meta_path.read_bytes()

    projection = project.module_diagram("focus_trees")

    assert projection["schema"] == "paradev.sdk.module_diagram.v1"
    assert projection["provider_schema"] == FOCUS_TREE_DIAGRAM_PROJECTION_SCHEMA
    assert projection["family"] == "focus_tree"
    assert projection["editable"] is True
    nodes = {str(row["id"]): row for row in projection["nodes"] if isinstance(row, dict)}
    assert (nodes["FOCUS_B"]["x"], nodes["FOCUS_B"]["y"]) == (1, 1)
    assert nodes["FOCUS_A"]["name_key"] == "FOCUS_A"
    assert nodes["FOCUS_A"]["localized_titles"] == {
        "l_english": "Authored Alpha",
        "l_simp_chinese": "源始阿尔法",
    }
    assert nodes["FOCUS_A"]["localized_descriptions"] == {
        "l_english": "Authored Alpha description",
    }
    assert nodes["FOCUS_B"]["localized_titles"] == {
        "l_english": "Authored Beta",
    }
    assert nodes["FOCUS_DON'T"]["name_key"] == "FOCUS_DON_T"
    assert nodes["FOCUS_DON'T"]["localized_titles"] == {
        "l_english": "Authored apostrophe focus",
    }
    assert nodes["FOCUS_DON'T"]["localized_descriptions"] == {
        "l_english": "Authored apostrophe description",
    }
    assert "Metadata fallback is forbidden" not in str(nodes)
    assert {(row["kind"], row["source"], row["target"]) for row in projection["edges"]} == {("prerequisite", "FOCUS_A", "FOCUS_B")}

    position_intents = [
        {
            "focus_id": "FOCUS_B",
            "x": 7,
            "y": 4,
            "source_revision": nodes["FOCUS_B"]["source_revision"],
        }
    ]
    edge_intents = [
        {
            "kind": "mutually_exclusive",
            "source_id": "FOCUS_B",
            "target_id": "FOCUS_C",
            "present": True,
            "source_revision": nodes["FOCUS_B"]["source_revision"],
        },
        {
            "kind": "prerequisite",
            "source_id": "FOCUS_A",
            "target_id": "FOCUS_B",
            "present": False,
            "source_revision": nodes["FOCUS_B"]["source_revision"],
        },
    ]
    plan = project.edit_module_diagram(
        "focus_tree",
        position_intents=position_intents,
        edge_intents=edge_intents,
    )

    assert plan["schema"] == "paradev.sdk.module_diagram_edit.v1"
    assert plan["provider_schema"] == "paradev.hoi4.focus-tree-diagram-plan.v1"
    assert plan["status"] == "planned"
    assert plan["blocked"] is False
    assert plan["written"] is False
    assert [row["path"] for row in plan["drafts"]] == ["src/modules/focus_tree/TEST_TREE/def.txt"]
    assert meta_path.read_bytes() == before_meta

    applied = project.edit_module_diagram(
        "focus_trees",
        position_intents=position_intents,
        edge_intents=edge_intents,
        write=True,
        plan_hash=str(plan["plan_hash"]),
    )

    assert applied["status"] == "applied"
    assert applied["blocked"] is False
    assert applied["applied"] is True
    assert applied["written"] is True
    assert applied["validation"]["family"] == "focus_tree"
    assert applied["validation"]["blocked"] is False
    assert applied["catalog_mutation"]["schema"] == ("paradev.hb.catalog-mutation.v1")
    assert meta_path.read_bytes() == before_meta
    text = source_path.read_text(encoding="utf-8")
    assert "x = 7" in text
    assert "y = 4" in text
    assert text.count("mutually_exclusive = {") == 2
    assert "prerequisite = {" not in text

    result = project.build(family="focus_tree", emit_artifacts=True)

    assert result.blocked is False
    emitted = project.output_root / "common/national_focus/TEST_TREE.txt"
    assert emitted.is_file()
    assert "x = 7" in emitted.read_text(encoding="utf-8")


def test_project_creates_one_focus_with_exact_two_file_transaction(
    tmp_path: Path,
) -> None:
    project = _write_focus_tree_project(tmp_path)
    tree_root = tmp_path / "src/modules/focus_tree/TEST_TREE"
    def_path = tree_root / "def.txt"
    loc_path = tree_root / "main.loc"
    meta_path = tree_root / "meta.yaml"
    before_def = def_path.read_bytes()
    before_loc = loc_path.read_bytes()
    before_meta = meta_path.read_bytes()
    projection = project.module_diagram("focus_tree")
    tree = next(row for row in projection["trees"] if row["id"] == "TEST_TREE")
    request = {
        "tree_id": "TEST_TREE",
        "focus_id": "FOCUS_NEW",
        "x": 2,
        "y": 3,
        "title": "A New Direction",
        "description": "First line.\nSecond line.",
        "source_revision": tree["source_revision"],
        "relative_position_id": "FOCUS_A",
        "prerequisite_id": "FOCUS_A",
    }

    plan = project.edit_module_diagram("focus_tree", node_intents=[request])

    assert plan["schema"] == "paradev.sdk.module_diagram_edit.v1"
    assert plan["provider_schema"] == FOCUS_TREE_NODE_CREATION_PLAN_SCHEMA
    assert plan["status"] == "planned"
    assert plan["blocked"] is False
    assert plan["written"] is False
    assert [row["path"] for row in plan["drafts"]] == [
        "src/modules/focus_tree/TEST_TREE/def.txt",
        "src/modules/focus_tree/TEST_TREE/main.loc",
    ]
    assert plan["absent_file_targets"] == [
        {
            "path": "src/modules/focus_tree/TEST_TREE/icons/FOCUS_NEW.png",
            "kind": "focus_preview_png",
            "content_type": "image/png",
            "precondition": "absent",
            "write": False,
        }
    ]
    assert def_path.read_bytes() == before_def
    assert loc_path.read_bytes() == before_loc
    assert meta_path.read_bytes() == before_meta
    assert plan["intent"]["localization_source_revision"]

    applied = project.edit_module_diagram(
        "focus_tree",
        node_intents=[request],
        write=True,
        plan_hash=str(plan["plan_hash"]),
    )

    assert applied["status"] == "applied"
    assert applied["blocked"] is False
    assert applied["written"] is True
    assert applied["validation"]["family"] == "focus_tree"
    assert applied["validation"]["blocked"] is False
    assert applied["catalog_mutation"]["schema"] == "paradev.hb.catalog-mutation.v1"
    assert meta_path.read_bytes() == before_meta
    assert not (tree_root / "icons/FOCUS_NEW.png").exists()
    assert "id = FOCUS_NEW" in def_path.read_text(encoding="utf-8")
    assert "relative_position_id = FOCUS_A" in def_path.read_text(encoding="utf-8")
    assert "[en.FOCUS_NEW]\nA New Direction" in loc_path.read_text(encoding="utf-8")
    refreshed = project.module_diagram("focus_tree")
    created = next(row for row in refreshed["nodes"] if row["id"] == "FOCUS_NEW")
    assert created["localized_titles"] == {"l_english": "A New Direction"}
    assert created["localized_descriptions"] == {
        "l_english": "First line.\nSecond line.",
    }


def test_project_focus_creation_rolls_back_both_sources_on_build_rejection(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _write_focus_tree_project(tmp_path)
    tree_root = tmp_path / "src/modules/focus_tree/TEST_TREE"
    def_path = tree_root / "def.txt"
    loc_path = tree_root / "main.loc"
    before_def = def_path.read_bytes()
    before_loc = loc_path.read_bytes()
    projection = project.module_diagram("focus_tree")
    tree = next(row for row in projection["trees"] if row["id"] == "TEST_TREE")
    request = {
        "tree_id": "TEST_TREE",
        "focus_id": "FOCUS_REJECTED",
        "x": 4,
        "y": 5,
        "title": "Rejected Focus",
        "description": "This draft must roll back.",
        "source_revision": tree["source_revision"],
    }
    plan = project.edit_module_diagram("focus_tree", node_intents=[request])

    def rejected_build(
        _project: Project,
        **_kwargs: object,
    ) -> BuildResult:
        return BuildResult.plan(
            "focus_tree_diagram",
            profile="hoi4",
            diagnostics=(
                Diagnostic(
                    code="test.build_rejected",
                    message="Synthetic focus creation rejection.",
                ),
            ),
        )

    monkeypatch.setattr(Project, "build", rejected_build)
    rejected = project.edit_module_diagram(
        "focus_tree",
        node_intents=[request],
        write=True,
        plan_hash=str(plan["plan_hash"]),
    )

    assert rejected["status"] == "blocked"
    assert rejected["written"] is False
    assert any(row["code"] == "module_diagram.build_rejected" for row in rejected["diagnostics"])
    assert def_path.read_bytes() == before_def
    assert loc_path.read_bytes() == before_loc


def test_project_focus_creation_treats_target_directory_as_occupied(
    tmp_path: Path,
) -> None:
    project = _write_focus_tree_project(tmp_path)
    tree_root = tmp_path / "src/modules/focus_tree/TEST_TREE"
    (tree_root / "icons/FOCUS_BLOCKED.png").mkdir(parents=True)
    projection = project.module_diagram("focus_tree")
    tree = next(row for row in projection["trees"] if row["id"] == "TEST_TREE")

    plan = project.edit_module_diagram(
        "focus_tree",
        node_intents=[
            {
                "tree_id": "TEST_TREE",
                "focus_id": "FOCUS_BLOCKED",
                "x": 1,
                "y": 2,
                "title": "Blocked Focus",
                "description": "A directory already occupies the preview path.",
                "source_revision": tree["source_revision"],
            }
        ],
    )

    assert plan["status"] == "blocked"
    assert plan["drafts"] == []
    assert plan["absent_file_targets"] == []
    assert [row["code"] for row in plan["diagnostics"]] == [
        "focus_tree.create.image_target_exists",
    ]


def test_project_focus_creation_caps_filesystem_inventory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _write_focus_tree_project(tmp_path)
    projection = project.module_diagram("focus_tree")
    tree = next(row for row in projection["trees"] if row["id"] == "TEST_TREE")
    monkeypatch.setattr(
        "paradev.games.hoi4.diagram_providers.MAX_FOCUS_TREE_NODE_CREATION_OCCUPIED_PATHS",
        2,
    )

    with pytest.raises(ValueError, match="inventory exceeds the 2-entry"):
        project.edit_module_diagram(
            "focus_tree",
            node_intents=[
                {
                    "tree_id": "TEST_TREE",
                    "focus_id": "FOCUS_LIMITED",
                    "x": 1,
                    "y": 2,
                    "title": "Limited Focus",
                    "description": "The inventory limit must fail closed.",
                    "source_revision": tree["source_revision"],
                }
            ],
        )


@pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="POSIX FIFO is unavailable")
def test_project_focus_creation_rejects_non_regular_inventory_entry(
    tmp_path: Path,
) -> None:
    project = _write_focus_tree_project(tmp_path)
    tree_root = tmp_path / "src/modules/focus_tree/TEST_TREE"
    os.mkfifo(tree_root / "unexpected.pipe")
    projection = project.module_diagram("focus_tree")
    tree = next(row for row in projection["trees"] if row["id"] == "TEST_TREE")

    with pytest.raises(ValueError, match="not a regular file"):
        project.edit_module_diagram(
            "focus_tree",
            node_intents=[
                {
                    "tree_id": "TEST_TREE",
                    "focus_id": "FOCUS_FIFO",
                    "x": 1,
                    "y": 2,
                    "title": "FIFO Focus",
                    "description": "Non-regular inventory entries must fail closed.",
                    "source_revision": tree["source_revision"],
                }
            ],
        )


def test_project_technology_diagram_rejects_stale_source_revision(
    tmp_path: Path,
) -> None:
    project = _write_technology_project(tmp_path)
    alpha_path = tmp_path / "src/modules/technology/TECH_ALPHA - Alpha/def.txt"
    projection = project.module_diagram("technology")
    alpha = next(row for row in projection["nodes"] if row["id"] == "TECH_ALPHA")
    intents = [
        {
            "technology_id": "TECH_ALPHA",
            "x": 7,
            "y": 8,
            "source_revision": alpha["source_revision"],
        }
    ]
    plan = project.edit_module_diagram(
        "technology",
        position_intents=intents,
    )
    alpha_path.write_text(
        alpha_path.read_text(encoding="utf-8") + "# external edit\n",
        encoding="utf-8",
    )

    stale = project.edit_module_diagram(
        "technology",
        position_intents=intents,
        write=True,
        plan_hash=str(plan["plan_hash"]),
    )

    assert stale["status"] == "blocked"
    assert stale["written"] is False
    assert any(row["code"] == "technology.plan.source_revision_mismatch" for row in stale["diagnostics"])
    assert alpha_path.read_text(encoding="utf-8").endswith("# external edit\n")
    assert "x = 7" not in alpha_path.read_text(encoding="utf-8")


def test_project_technology_diagram_rolls_back_build_rejection(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _write_technology_project(tmp_path)
    beta_path = tmp_path / "src/modules/technology/TECH_BETA - Beta/def.txt"
    before = beta_path.read_bytes()
    projection = project.module_diagram("technology")
    beta = next(row for row in projection["nodes"] if row["id"] == "TECH_BETA")
    intents = [
        {
            "technology_id": "TECH_BETA",
            "x": 12,
            "y": 6,
            "source_revision": beta["source_revision"],
        }
    ]
    plan = project.edit_module_diagram(
        "technology",
        position_intents=intents,
    )

    def rejected_build(
        _project: Project,
        **_kwargs: object,
    ) -> BuildResult:
        return BuildResult.plan(
            "technology_diagram",
            profile="hoi4",
            diagnostics=(
                Diagnostic(
                    code="test.build_rejected",
                    message="Synthetic family build rejection.",
                ),
            ),
        )

    monkeypatch.setattr(Project, "build", rejected_build)

    rejected = project.edit_module_diagram(
        "technology",
        position_intents=intents,
        write=True,
        plan_hash=str(plan["plan_hash"]),
    )

    assert rejected["status"] == "blocked"
    assert rejected["written"] is False
    assert any(row["code"] == "module_diagram.build_rejected" for row in rejected["diagnostics"])
    assert beta_path.read_bytes() == before


def test_project_focus_tree_diagram_rolls_back_build_rejection(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _write_focus_tree_project(tmp_path)
    source_path = tmp_path / "src/modules/focus_tree/TEST_TREE/def.txt"
    before = source_path.read_bytes()
    projection = project.module_diagram("focus_tree")
    focus = next(row for row in projection["nodes"] if row["id"] == "FOCUS_B")
    intents = [
        {
            "focus_id": "FOCUS_B",
            "x": 12,
            "y": 6,
            "source_revision": focus["source_revision"],
        }
    ]
    plan = project.edit_module_diagram(
        "focus_tree",
        position_intents=intents,
    )

    def rejected_build(
        _project: Project,
        **_kwargs: object,
    ) -> BuildResult:
        return BuildResult.plan(
            "focus_tree_diagram",
            profile="hoi4",
            diagnostics=(
                Diagnostic(
                    code="test.build_rejected",
                    message="Synthetic focus-tree family build rejection.",
                ),
            ),
        )

    monkeypatch.setattr(Project, "build", rejected_build)

    rejected = project.edit_module_diagram(
        "focus_tree",
        position_intents=intents,
        write=True,
        plan_hash=str(plan["plan_hash"]),
    )

    assert rejected["status"] == "blocked"
    assert rejected["written"] is False
    assert any(row["code"] == "module_diagram.build_rejected" for row in rejected["diagnostics"])
    assert source_path.read_bytes() == before


def test_project_focus_tree_diagram_requires_exact_plan_hash_before_writing(
    tmp_path: Path,
) -> None:
    project = _write_focus_tree_project(tmp_path)
    source_path = tmp_path / "src/modules/focus_tree/TEST_TREE/def.txt"
    before = source_path.read_bytes()
    projection = project.module_diagram("focus_tree")
    focus = next(row for row in projection["nodes"] if row["id"] == "FOCUS_B")
    intents = [
        {
            "focus_id": "FOCUS_B",
            "x": 10,
            "y": 5,
            "source_revision": focus["source_revision"],
        }
    ]
    plan = project.edit_module_diagram(
        "focus_tree",
        position_intents=intents,
    )

    missing = project.edit_module_diagram(
        "focus_tree",
        position_intents=intents,
        write=True,
    )
    mismatched = project.edit_module_diagram(
        "focus_tree",
        position_intents=intents,
        write=True,
        plan_hash=f"{plan['plan_hash']}-stale",
    )

    assert missing["status"] == "blocked"
    assert [row["code"] for row in missing["diagnostics"]] == ["module_diagram.plan_hash_required"]
    assert mismatched["status"] == "blocked"
    assert [row["code"] for row in mismatched["diagnostics"]] == ["module_diagram.plan_hash_mismatch"]
    assert source_path.read_bytes() == before


def test_project_technology_diagram_bounds_direct_sdk_intents(
    tmp_path: Path,
) -> None:
    project = _write_technology_project(tmp_path)

    with pytest.raises(
        ValueError,
        match=("Module diagram edge_intents cannot contain more than " f"{MAX_MODULE_DIAGRAM_EDGE_INTENTS} intents"),
    ):
        project.edit_module_diagram(
            "technology",
            edge_intents=[{} for _ in range(MAX_MODULE_DIAGRAM_EDGE_INTENTS + 1)],
        )
