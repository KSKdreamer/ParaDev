from __future__ import annotations

from collections import Counter
from dataclasses import replace

from heavenbase.utils import dumps_json, pj

from paradev.build import (
    LocalizationEntry,
    ModuleSourceBundle,
    PDXBlockSource,
    load_module_sources,
)
from paradev.games.hoi4 import MIO_TRAIT_PROJECTION_SCHEMA, mio_trait_projection
from paradev.games.hoi4.diagram_providers import MIO_DIAGRAM_PROVIDER
from paradev.pdx import PDXBlock

MIO_FIXTURE_ROOT = pj("tests", "fixtures", "hoi4_mio", abs=True)


def test_mio_diagram_starts_from_the_complete_project_projection() -> None:
    assert MIO_DIAGRAM_PROVIDER.initial_scope == "project"
    assert MIO_DIAGRAM_PROVIDER.to_view()["initial_scope"] == "project"


def test_mio_trait_projection_reads_positions_edges_localization_and_icons() -> None:
    payload = mio_trait_projection(_mio_fixture_bundle("organizations.txt", loc=True))

    assert payload["schema"] == MIO_TRAIT_PROJECTION_SCHEMA
    assert payload["source_kind"] == "compiled_pdx"
    assert payload["editable"] is False
    assert payload["summary"] == {
        "organization_count": 2,
        "trait_count": 7,
        "initial_trait_count": 2,
        "positioned_trait_count": 5,
        "edge_count": 8,
        "edge_counts": {
            "all_parent": 2,
            "any_parent": 2,
            "mutually_exclusive": 1,
            "relative_position": 3,
        },
        "diagnostic_count": 0,
    }
    organization = payload["organizations"][0]
    organization_id = "C01_Imperial_Royal_Airship_Manufacturing organization"
    assert organization["organization_id"] == organization_id
    assert organization["name_key"] == "C01_airship_organization"
    assert organization["localized_titles"] == {
        "l_english": "Royal Airship Manufacturer",
        "l_simp_chinese": "皇家飞船制造商",
    }
    assert organization["icon"] == "GFX_idea_generic_air_manufacturer_2"
    assert organization["trait_count"] == 3

    traits = {(row["organization_id"], row["kind"], row.get("token") or row["name_key"]): row for row in payload["traits"]}
    initial = traits[
        (
            organization_id,
            "initial_trait",
            "generic_mio_initial_trait_heavy_aircraft_designer",
        )
    ]
    assert initial["localized_titles"]["l_english"] == "Heavy Aircraft Designer"
    standardized = traits[(organization_id, "trait", "standardized_alloys_trait")]
    assert standardized["position"] == {"x": 0, "y": 1}
    assert standardized["relative_position_id"] == "shared_root_trait"
    assert standardized["any_parent_ids"] == ["shared_root_trait"]
    assert standardized["mutually_exclusive_ids"] == ["quality_alloys_trait"]
    assert standardized["icon"] == "GFX_generic_mio_trait_icon_resources"
    assert standardized["localized_titles"]["l_english"] == "Standardized Alloys"
    assert standardized["source_path"] == "organizations.txt"
    assert standardized["source_span"]["line"] > 1

    edges = {(row["kind"], row["source"], row["target"]) for row in payload["edges"]}
    assert (
        "relative_position",
        _trait_node_id(organization_id, "shared_root_trait"),
        _trait_node_id(organization_id, "standardized_alloys_trait"),
    ) in edges
    assert (
        "any_parent",
        _trait_node_id(organization_id, "shared_root_trait"),
        _trait_node_id(organization_id, "standardized_alloys_trait"),
    ) in edges
    exclusive_pair = sorted(
        (
            _trait_node_id(organization_id, "standardized_alloys_trait"),
            _trait_node_id(organization_id, "quality_alloys_trait"),
        )
    )
    assert (
        "mutually_exclusive",
        exclusive_pair[0],
        exclusive_pair[1],
    ) in edges
    dumps_json(payload, ensure_ascii=False, sort_keys=True)


def test_mio_trait_projection_is_deterministic_metadata_independent_and_owned() -> None:
    bundle = _mio_fixture_bundle("organizations.txt", loc=True)
    source_before = bundle.pdx_sources[0].block.dump()

    payload = mio_trait_projection(bundle)

    assert payload == mio_trait_projection(bundle)
    assert payload == mio_trait_projection(
        replace(
            bundle,
            metadata={
                "settings": {
                    "organization_ids": ["wrong"],
                    "trait_tokens": ["wrong"],
                }
            },
        )
    )
    assert bundle.pdx_sources[0].block.dump() == source_before
    shared_roots = [row for row in payload["traits"] if row.get("token") == "shared_root_trait"]
    assert {row["organization_id"] for row in shared_roots} == {
        "C01_Imperial_Royal_Airship_Manufacturing organization",
        "generic_second_organization",
    }
    assert len({row["id"] for row in shared_roots}) == 2
    quality = next(row for row in payload["traits"] if row.get("token") == "quality_alloys_trait")
    assert quality["all_parent_ids"] == [
        "shared_root_trait",
        "standardized_alloys_trait",
    ]
    assert len([edge for edge in payload["edges"] if edge["kind"] == "all_parent" and edge["target"] == quality["id"]]) == 2
    assert payload["nodes"] == payload["traits"]


def test_mio_trait_projection_aggregates_module_family_in_stable_order() -> None:
    organizations = replace(
        _mio_fixture_bundle("organizations.txt", loc=True),
        module_id="military_industrial_organization_component/z_organizations",
    )
    includes = replace(
        _mio_fixture_bundle("debug_organizations.txt"),
        module_id="military_industrial_organization_component/a_includes",
    )

    payload = mio_trait_projection((organizations, includes))

    assert payload == mio_trait_projection((includes, organizations))
    assert payload["module_ids"] == [
        "military_industrial_organization_component/a_includes",
        "military_industrial_organization_component/z_organizations",
    ]
    assert "module_id" not in payload
    assert payload["summary"]["organization_count"] == 4
    assert payload["summary"]["trait_count"] == 7
    assert len(payload["nodes"]) == 7
    assert {row["module_id"] for row in payload["organizations"]} == {
        "military_industrial_organization_component/a_includes",
        "military_industrial_organization_component/z_organizations",
    }


def test_mio_trait_projection_exposes_includes_without_inventing_inherited_traits() -> None:
    payload = mio_trait_projection(_mio_fixture_bundle("debug_organizations.txt"))

    assert payload["summary"]["organization_count"] == 2
    assert payload["summary"]["trait_count"] == 0
    assert payload["traits"] == []
    assert payload["edges"] == []
    assert payload["diagnostics"] == []
    organizations = {row["organization_id"]: row for row in payload["organizations"]}
    assert organizations["DEBUG_generic_tank_organization"]["include_id"] == "generic_tank_organization"


def test_mio_trait_projection_reports_ambiguous_or_unresolved_source_records() -> None:
    source = PDXBlockSource(
        slot="pdx",
        path="common/military_industrial_organization/organizations/malformed.txt",
        block=PDXBlock.from_str("""
            policy_record = {
                icon = GFX_policy
                allowed = { always = yes }
            }
            organization = {
                trait = {
                    name = shared_trait
                    icon = GFX_trait
                    position = { x = @dynamic_x y = 1 }
                    relative_position_id = missing_relative
                    any_parent = { missing_parent }
                }
                trait = {
                    token = shared_trait
                    name = shared_trait
                }
                trait = {
                    position = { x = 0 y = 0 }
                }
            }
            """),
    )
    bundle = ModuleSourceBundle(
        root=".",
        source_slots={"pdx": (source.path,), "loc": ("main.loc",)},
        metadata={"type": "military_industrial_organization_component"},
        pdx_sources=(source,),
        loc_entries=(
            LocalizationEntry(
                key="shared_trait",
                language="l_english",
                text="Shared trait",
                source_path="main.loc",
                module_id="military_industrial_organization_component/malformed",
            ),
        ),
        module_id="military_industrial_organization_component/malformed",
    )

    payload = mio_trait_projection(bundle)

    assert payload["summary"]["organization_count"] == 1
    assert payload["summary"]["trait_count"] == 1
    assert payload["traits"][0]["localized_titles"] == {"l_english": "Shared trait"}
    assert payload["traits"][0]["icon"] == "GFX_trait"
    assert "position" not in payload["traits"][0]
    assert payload["edges"] == []
    codes = Counter(row["code"] for row in payload["diagnostics"])
    assert codes == {
        "mio.trait_duplicate_id": 1,
        "mio.trait_missing_id": 1,
        "mio.trait_missing_token": 1,
        "mio.trait_position_unresolved": 1,
        "mio.trait_relationship_unresolved": 2,
    }
    assert {row["severity"] for row in payload["diagnostics"]} == {
        "error",
        "warning",
    }


def _mio_fixture_bundle(pdx_path: str, *, loc: bool = False) -> ModuleSourceBundle:
    source_slots: dict[str, tuple[str, ...]] = {"pdx": (pdx_path,)}
    if loc:
        source_slots["loc"] = ("main.loc",)
    return load_module_sources(
        MIO_FIXTURE_ROOT,
        source_slots,
        module_id="military_industrial_organization_component/fixture",
        inferred_type="military_industrial_organization_component",
    )


def _trait_node_id(organization_id: str, token: str) -> str:
    return f"{organization_id}::trait::{token}"
