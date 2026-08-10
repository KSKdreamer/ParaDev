from __future__ import annotations

import math

import pytest
from heavenbase.utils import load_txt, pj

from paradev.games.hoi4 import (
    MIO_TRAIT_CREATION_PLAN_SCHEMA,
    MIO_TRAIT_DIAGRAM_PLAN_SCHEMA,
    MIO_TRAIT_DIAGRAM_PROJECTION_SCHEMA,
    MIOTraitEdgeIntent,
    MIOTraitLocalizationSource,
    MIOTraitPositionIntent,
    MIOTraitSource,
    mio_trait_diagram_projection,
    plan_mio_trait_creation,
    plan_mio_trait_diagram_edits,
)
from paradev.pdx import parse_pdx

MIO_FIXTURE_ROOT = pj("tests", "fixtures", "hoi4_mio", abs=True)
ORGANIZATION_ID = "C01_Imperial_Royal_Airship_Manufacturing organization"


def test_source_projection_is_exact_editable_and_organization_scoped() -> None:
    source = MIOTraitSource(
        path="src/modules/mio/example/def.txt",
        text=load_txt(
            pj(MIO_FIXTURE_ROOT, "organizations.txt"),
            encoding="utf-8",
        ),
    )

    payload = mio_trait_diagram_projection([source])

    assert payload["schema"] == MIO_TRAIT_DIAGRAM_PROJECTION_SCHEMA
    assert payload["source_kind"] == "module_pdx_source"
    assert payload["editable"] is True
    assert payload["diagnostics"] == []
    assert payload["summary"] == {
        "source_count": 1,
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
    revision = payload["sources"][0]["source_revision"]
    assert revision.startswith("sha256:")
    assert len(revision) == 71
    standardized = next(row for row in payload["nodes"] if row.get("trait_id") == "standardized_alloys_trait")
    assert standardized["organization_id"] == ORGANIZATION_ID
    assert standardized["position"] == {"x": 0, "y": 1}
    assert standardized["source_revision"] == revision
    assert standardized["editable"] is True
    assert {
        (
            row["kind"],
            row["organization_id"],
            row["source_trait_id"],
            row["target_trait_id"],
        )
        for row in payload["edges"]
    } >= {
        (
            "relative_position",
            ORGANIZATION_ID,
            "shared_root_trait",
            "standardized_alloys_trait",
        ),
        (
            "mutually_exclusive",
            ORGANIZATION_ID,
            "quality_alloys_trait",
            "standardized_alloys_trait",
        ),
    }
    exclusive = next(row for row in payload["edges"] if row["kind"] == "mutually_exclusive")
    assert exclusive["declaration_count"] == 2
    assert exclusive["reciprocal"] is True
    assert payload == mio_trait_diagram_projection([source])


def test_trait_creation_plans_exact_definition_and_localization_drafts() -> None:
    source_path = "src/modules/mio/example/def.txt"
    localization_path = "src/modules/mio/example/main.loc"
    source = MIOTraitSource(
        source_path,
        load_txt(
            pj(MIO_FIXTURE_ROOT, "organizations.txt"),
            encoding="utf-8",
        ),
    )
    localization = MIOTraitLocalizationSource(
        localization_path,
        load_txt(
            pj(MIO_FIXTURE_ROOT, "main.loc"),
            encoding="utf-8",
        ),
    )
    projection = mio_trait_diagram_projection([source])
    parent = next(row for row in projection["nodes"] if row.get("trait_id") == "standardized_alloys_trait")

    plan = plan_mio_trait_creation(
        [source],
        localization_sources=[localization],
        localization_path=localization_path,
        intent={
            "organization_id": parent["organization_id"],
            "parent_trait_id": parent["trait_id"],
            "trait_id": "precision_tools_trait",
            "title": "Precision Tools",
            "icon": "GFX_generic_mio_trait_icon_reliability",
            "x": 0,
            "y": 2,
            "bonus_key": "reliability",
            "bonus_value": 0.05,
            "language": "en",
            "source_path": source_path,
            "source_revision": parent["source_revision"],
        },
    )

    assert plan["schema"] == MIO_TRAIT_CREATION_PLAN_SCHEMA
    assert plan["status"] == "planned"
    assert plan["diagnostics"] == []
    assert plan["summary"] == {
        "node_intent_count": 1,
        "replacement_count": 2,
        "draft_count": 2,
        "diagnostic_count": 0,
    }
    drafts = {row["path"]: row["text"] for row in plan["drafts"]}
    definition = drafts[source_path]
    assert "token = precision_tools_trait" in definition
    assert "relative_position_id = standardized_alloys_trait" in definition
    assert "reliability = 0.05" in definition
    parse_pdx(definition)
    assert "[l_english.precision_tools_trait]\n" "Precision Tools\n" in drafts[localization_path]


def test_plan_preserves_bom_crlf_comments_and_unrelated_source() -> None:
    text = _editable_source().replace("\n", "\r\n")
    text = "\ufeff" + text
    source = MIOTraitSource("src/modules/mio/example/def.txt", text)
    projection = mio_trait_diagram_projection([source])
    revision = projection["sources"][0]["source_revision"]
    positions = [
        MIOTraitPositionIntent(
            organization_id="example_org",
            trait_id="trait_b",
            x=4.5,
            y=-3,
            source_revision=revision,
        )
    ]
    edges = [
        MIOTraitEdgeIntent(
            kind="relative_position",
            organization_id="example_org",
            source_id="trait_a",
            target_id="trait_b",
            present=False,
            source_revision=revision,
        ),
        MIOTraitEdgeIntent(
            kind="relative_position",
            organization_id="example_org",
            source_id="trait_c",
            target_id="trait_b",
            present=True,
            source_revision=revision,
        ),
        MIOTraitEdgeIntent(
            kind="any_parent",
            organization_id="example_org",
            source_id="trait_a",
            target_id="trait_b",
            present=False,
            source_revision=revision,
        ),
        MIOTraitEdgeIntent(
            kind="any_parent",
            organization_id="example_org",
            source_id="trait_c",
            target_id="trait_b",
            present=True,
            source_revision=revision,
        ),
        MIOTraitEdgeIntent(
            kind="all_parent",
            organization_id="example_org",
            source_id="trait_a",
            target_id="trait_b",
            present=False,
            source_revision=revision,
        ),
        MIOTraitEdgeIntent(
            kind="mutually_exclusive",
            organization_id="example_org",
            source_id="trait_a",
            target_id="trait_b",
            present=True,
            source_revision=revision,
        ),
    ]

    plan = plan_mio_trait_diagram_edits(
        [source],
        position_intents=positions,
        edge_intents=edges,
    )
    reversed_plan = plan_mio_trait_diagram_edits(
        [source],
        position_intents=list(reversed(positions)),
        edge_intents=list(reversed(edges)),
    )

    assert plan["schema"] == MIO_TRAIT_DIAGRAM_PLAN_SCHEMA
    assert plan["projection_schema"] == MIO_TRAIT_DIAGRAM_PROJECTION_SCHEMA
    assert plan["status"] == "planned"
    assert plan["write"] is False
    assert plan["diagnostics"] == []
    assert plan == reversed_plan
    assert plan["summary"] == {
        "position_intent_count": 1,
        "edge_intent_count": 6,
        "replacement_count": 8,
        "draft_count": 1,
        "diagnostic_count": 0,
    }
    draft = plan["drafts"][0]["text"]
    assert draft.startswith("\ufeff# exact header\r\n")
    assert "\n" not in draft.replace("\r\n", "")
    assert "x = 4.5 # keep coordinate note\r\n" in draft
    assert "y = -3\r\n" in draft
    assert "relative_position_id = trait_c\r\n" in draft
    assert "any_parent = {\r\n            trait_c\r\n" in draft
    assert "all_parents" not in draft
    assert "mutually_exclusive = {\r\n            trait_c\r\n            trait_a\r\n" in draft
    assert (
        "token = trait_a\r\n"
        "        name = trait_a\r\n"
        "        position = {\r\n"
        "            x = 0\r\n"
        "            y = 0\r\n"
        "        }\r\n"
        "        mutually_exclusive = {\r\n"
        "            trait_b\r\n"
        "        }\r\n" in draft
    )
    assert "untouched = {\r\n            exact_spacing    =    yes\r\n" "        }\r\n" in draft
    parse_pdx(draft)
    assert plan["drafts"][0]["expected_source_revision"] == revision
    assert plan["drafts"][0]["source_revision"] != revision
    assert len(plan["plan_hash"]) == 64


@pytest.mark.parametrize(
    ("text", "expected_code"),
    [
        (
            """
            duplicate_org = { include = generic_mio }
            duplicate_org = { include = generic_mio }
            """,
            "mio.source.organization_duplicate",
        ),
        (
            """
            example_org = {
                trait = { token = duplicate position = { x = 0 y = 0 } }
                trait = { token = duplicate position = { x = 1 y = 0 } }
            }
            """,
            "mio.source.trait_duplicate",
        ),
        (
            """
            example_org = {
                trait = {
                    token = trait_a
                    position = { x = 0 y = 0 }
                    any_parent = trait_b
                }
                trait = { token = trait_b position = { x = 1 y = 0 } }
            }
            """,
            "mio.source.relationship_syntax_unsupported",
        ),
        (
            """
            example_org = {
                trait = {
                    token = trait_a
                    position = { x = 0 x = 1 y = 0 }
                }
            }
            """,
            "mio.source.coordinates_ambiguous",
        ),
        (
            "example_org = { trait = { token = broken ",
            "pdx.unclosed_block",
        ),
    ],
)
def test_projection_fails_closed_on_ambiguous_or_unsupported_source(
    text: str,
    expected_code: str,
) -> None:
    payload = mio_trait_diagram_projection([MIOTraitSource("mio/def.txt", text)])

    assert payload["editable"] is False
    assert expected_code in _diagnostic_codes(payload)
    plan = plan_mio_trait_diagram_edits([MIOTraitSource("mio/def.txt", text)])
    assert plan["status"] == "blocked"
    assert plan["drafts"] == []
    assert plan["source_replacements"] == []


def test_plan_rejects_stale_nonfinite_and_out_of_bounds_positions() -> None:
    source = MIOTraitSource("mio/def.txt", _editable_source())
    projection = mio_trait_diagram_projection([source])
    revision = projection["sources"][0]["source_revision"]

    stale = plan_mio_trait_diagram_edits(
        [source],
        position_intents=[
            MIOTraitPositionIntent(
                "example_org",
                "trait_b",
                1,
                2,
                "sha256:" + "0" * 64,
            )
        ],
    )
    nonfinite = plan_mio_trait_diagram_edits(
        [source],
        position_intents=[
            MIOTraitPositionIntent(
                "example_org",
                "trait_b",
                math.nan,
                2,
                revision,
            )
        ],
    )
    out_of_bounds = plan_mio_trait_diagram_edits(
        [source],
        position_intents=[
            MIOTraitPositionIntent(
                "example_org",
                "trait_b",
                100_001,
                2,
                revision,
            )
        ],
    )

    assert stale["status"] == "blocked"
    assert "mio.plan.source_revision_mismatch" in _diagnostic_codes(stale)
    assert nonfinite["status"] == "blocked"
    assert "mio.plan.invalid_position_intent" in _diagnostic_codes(nonfinite)
    assert out_of_bounds["status"] == "blocked"
    assert "mio.plan.position_out_of_bounds" in _diagnostic_codes(out_of_bounds)
    for plan in (stale, nonfinite, out_of_bounds):
        assert plan["drafts"] == []
        assert plan["source_replacements"] == []


def test_projection_and_plan_reject_cross_organization_references() -> None:
    cross_source = MIOTraitSource(
        "mio/def.txt",
        """
        first_org = {
            trait = {
                token = local_trait
                position = { x = 0 y = 0 }
                any_parent = { remote_trait }
            }
        }
        second_org = {
            trait = {
                token = remote_trait
                position = { x = 0 y = 0 }
            }
        }
        """,
    )
    projection = mio_trait_diagram_projection([cross_source])
    assert projection["editable"] is False
    assert "mio.source.relationship_cross_organization" in _diagnostic_codes(projection)

    clean_source = MIOTraitSource(
        "mio/def.txt",
        cross_source.text.replace(
            "                any_parent = { remote_trait }\n",
            "",
        ),
    )
    clean_projection = mio_trait_diagram_projection([clean_source])
    revision = clean_projection["sources"][0]["source_revision"]
    plan = plan_mio_trait_diagram_edits(
        [clean_source],
        edge_intents=[
            MIOTraitEdgeIntent(
                "any_parent",
                "first_org",
                "remote_trait",
                "local_trait",
                True,
                revision,
            )
        ],
    )
    assert plan["status"] == "blocked"
    assert "mio.plan.edge_cross_organization" in _diagnostic_codes(plan)
    assert plan["drafts"] == []


def test_comment_owned_relationship_removal_is_blocked_without_a_draft() -> None:
    text = _editable_source().replace(
        "            trait_a\n        }\n        all_parents",
        "            trait_a # authored reason\n        }\n        all_parents",
    )
    source = MIOTraitSource("mio/def.txt", text)
    projection = mio_trait_diagram_projection([source])
    revision = projection["sources"][0]["source_revision"]

    plan = plan_mio_trait_diagram_edits(
        [source],
        edge_intents=[
            MIOTraitEdgeIntent(
                "any_parent",
                "example_org",
                "trait_a",
                "trait_b",
                False,
                revision,
            )
        ],
    )

    assert plan["status"] == "blocked"
    assert "mio.plan.any_parent_unsafe" in _diagnostic_codes(plan)
    assert plan["drafts"] == []
    assert plan["source_replacements"] == []


def test_relative_parent_change_requires_explicit_old_parent_removal() -> None:
    source = MIOTraitSource("mio/def.txt", _editable_source())
    projection = mio_trait_diagram_projection([source])
    revision = projection["sources"][0]["source_revision"]

    plan = plan_mio_trait_diagram_edits(
        [source],
        edge_intents=[
            MIOTraitEdgeIntent(
                "relative_position",
                "example_org",
                "trait_c",
                "trait_b",
                True,
                revision,
            )
        ],
    )

    assert plan["status"] == "blocked"
    assert "mio.plan.relative_position_unsafe" in _diagnostic_codes(plan)
    assert plan["drafts"] == []


def test_multiple_authored_parent_groups_allow_removal_but_not_guessed_addition() -> None:
    source = MIOTraitSource(
        "common/military_industrial_organization/organizations/example.txt",
        """
        example_org = {
            trait = { token = trait_a position = { x = 0 y = 0 } }
            trait = { token = trait_c position = { x = 1 y = 0 } }
            trait = { token = trait_d position = { x = 2 y = 0 } }
            trait = {
                token = trait_b
                position = { x = 0 y = 1 }
                any_parent = { trait_a }
                any_parent = { trait_c }
                all_parents = { trait_a }
                all_parents = { trait_c }
            }
        }
        """,
    )
    projection = mio_trait_diagram_projection([source])
    revision = projection["sources"][0]["source_revision"]
    assert projection["editable"] is True
    assert projection["summary"]["edge_count"] == 4
    assert {
        (
            row["kind"],
            row["source_trait_id"],
            row["target_trait_id"],
        )
        for row in projection["edges"]
    } == {
        ("any_parent", "trait_a", "trait_b"),
        ("any_parent", "trait_c", "trait_b"),
        ("all_parent", "trait_a", "trait_b"),
        ("all_parent", "trait_c", "trait_b"),
    }
    relation_groups = {
        (
            row["kind"],
            row["source_trait_id"],
            row["target_trait_id"],
        ): row["relation_groups"]
        for row in projection["edges"]
    }
    assert relation_groups == {
        ("any_parent", "trait_a", "trait_b"): [
            {
                "owner_id": "example_org::trait::trait_b",
                "group_index": 0,
            }
        ],
        ("any_parent", "trait_c", "trait_b"): [
            {
                "owner_id": "example_org::trait::trait_b",
                "group_index": 1,
            }
        ],
        ("all_parent", "trait_a", "trait_b"): [
            {
                "owner_id": "example_org::trait::trait_b",
                "group_index": 0,
            }
        ],
        ("all_parent", "trait_c", "trait_b"): [
            {
                "owner_id": "example_org::trait::trait_b",
                "group_index": 1,
            }
        ],
    }

    removal = plan_mio_trait_diagram_edits(
        [source],
        edge_intents=[
            MIOTraitEdgeIntent(
                "any_parent",
                "example_org",
                "trait_a",
                "trait_b",
                False,
                revision,
            )
        ],
    )
    addition = plan_mio_trait_diagram_edits(
        [source],
        edge_intents=[
            MIOTraitEdgeIntent(
                "any_parent",
                "example_org",
                "trait_d",
                "trait_b",
                True,
                revision,
            )
        ],
    )

    assert removal["status"] == "planned"
    assert removal["diagnostics"] == []
    assert removal["drafts"][0]["text"].count("any_parent") == 1
    assert "any_parent = { trait_c }" in removal["drafts"][0]["text"]
    assert addition["status"] == "blocked"
    assert "mio.plan.any_parent_unsafe" in _diagnostic_codes(addition)
    assert addition["drafts"] == []


def test_source_contract_rejects_duplicate_paths_and_non_pdx_records() -> None:
    source = MIOTraitSource("mio/def.txt", _editable_source())
    duplicate = mio_trait_diagram_projection([source, source])
    wrong_name = mio_trait_diagram_projection([MIOTraitSource("mio/main.loc", _editable_source())])
    invalid_unicode = mio_trait_diagram_projection([MIOTraitSource("mio/def.txt", "\ud800")])

    assert duplicate["editable"] is False
    assert "mio.source.duplicate_path" in _diagnostic_codes(duplicate)
    assert wrong_name["editable"] is False
    assert "mio.source.not_txt" in _diagnostic_codes(wrong_name)
    assert invalid_unicode["editable"] is False
    assert "mio.source.invalid_unicode" in _diagnostic_codes(invalid_unicode)
    for unsafe_path in (
        "/absolute/organizations.txt",
        r"common\organizations.txt",
        "./common/organizations.txt",
        "common/../organizations.txt",
        "common//organizations.txt",
        "C:/common/organizations.txt",
    ):
        payload = mio_trait_diagram_projection([MIOTraitSource(unsafe_path, _editable_source())])
        assert payload["editable"] is False
        assert "mio.source.invalid_path" in _diagnostic_codes(payload)


def _editable_source() -> str:
    return """# exact header
example_org = {
    trait = {
        token = trait_a
        name = trait_a
        position = {
            x = 0
            y = 0
        }
    }
    trait = {
        token = trait_b
        name = trait_b
        position = {
            x = 1 # keep coordinate note
            y = 2
        }
        relative_position_id = trait_a
        any_parent = {
            trait_a
        }
        all_parents = {
            trait_a
        }
        mutually_exclusive = {
            trait_c
        }
        untouched = {
            exact_spacing    =    yes
        }
    }
    trait = {
        token = trait_c
        name = trait_c
        position = {
            x = 2
            y = 0
        }
    }
}
"""


def _diagnostic_codes(payload: dict[str, object]) -> set[str]:
    return {str(row["code"]) for row in payload["diagnostics"] if isinstance(row, dict)}
