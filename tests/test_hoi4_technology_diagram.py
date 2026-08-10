from __future__ import annotations

from heavenbase.utils import dumps_json, sha256hash

from paradev.games.hoi4.technology import (
    TECHNOLOGY_DIAGRAM_PLAN_SCHEMA,
    TECHNOLOGY_DIAGRAM_PROJECTION_SCHEMA,
    TechnologyEdgeIntent,
    TechnologyPositionIntent,
    TechnologySource,
    plan_technology_diagram_edits,
    technology_diagram_projection,
)


def test_technology_projection_reads_source_positions_and_both_edge_kinds_deterministically() -> None:
    sources = [
        TechnologySource("modules/technology/b/def.txt", _technology_source("TECH_B", x="4", y="5")),
        {
            "path": "modules/technology/a/def.txt",
            "text": _technology_source(
                "TECH_A",
                x="1",
                y="2",
                extra=(
                    "        dependencies = {\n"
                    "            ROOT = 1\n"
                    "        }\n"
                    "        path = {\n"
                    "            leads_to_tech = TECH_B\n"
                    "            research_cost_coeff = 2\n"
                    "        }\n"
                ),
            ),
        },
        TechnologySource("modules/technology/root/def.txt", _technology_source("ROOT", x="0", y="0")),
    ]

    projection = technology_diagram_projection(sources)

    assert projection["schema"] == TECHNOLOGY_DIAGRAM_PROJECTION_SCHEMA
    assert projection["source_kind"] == "module_def_pdx"
    assert projection["editable"] is True
    assert projection["summary"] == {
        "source_count": 3,
        "node_count": 3,
        "edge_count": 2,
        "edge_counts": {"dependency": 1, "path": 1},
        "diagnostic_count": 0,
    }
    assert [row["path"] for row in projection["sources"]] == [
        "modules/technology/a/def.txt",
        "modules/technology/b/def.txt",
        "modules/technology/root/def.txt",
    ]
    assert [(row["id"], row["folder"], row["x"], row["y"]) for row in projection["nodes"]] == [
        ("ROOT", "industry_folder", 0, 0),
        ("TECH_A", "industry_folder", 1, 2),
        ("TECH_B", "industry_folder", 4, 5),
    ]
    assert all(row["editable"] is True for row in projection["nodes"])
    assert all(row["source_span"]["line"] == 2 for row in projection["nodes"])
    assert [(row["kind"], row["source"], row["target"], row["owner_id"]) for row in projection["edges"]] == [
        ("dependency", "ROOT", "TECH_A", "TECH_A"),
        ("path", "TECH_A", "TECH_B", "TECH_A"),
    ]
    assert projection == technology_diagram_projection(list(reversed(sources)))
    dumps_json(projection, ensure_ascii=False, sort_keys=True)


def test_position_plan_preserves_bom_crlf_comments_and_equal_numeric_spelling() -> None:
    text = "\ufeff" + _technology_source("TECH_A", x="1.000", y="-0.0 # keep this note").replace("\n", "\r\n")
    source = TechnologySource("modules/technology/a/def.txt", text)
    projection = technology_diagram_projection([source])
    revision = projection["nodes"][0]["source_revision"]

    plan = plan_technology_diagram_edits(
        [source],
        position_intents=[
            TechnologyPositionIntent(
                technology_id="TECH_A",
                x=1.0,
                y=3.25,
                source_revision=revision,
            )
        ],
    )

    assert plan["schema"] == TECHNOLOGY_DIAGRAM_PLAN_SCHEMA
    assert plan["projection_schema"] == TECHNOLOGY_DIAGRAM_PROJECTION_SCHEMA
    assert plan["status"] == "planned"
    assert plan["offset_unit"] == "unicode_codepoint"
    assert plan["summary"] == {
        "position_intent_count": 1,
        "edge_intent_count": 0,
        "replacement_count": 1,
        "draft_count": 1,
        "diagnostic_count": 0,
    }
    expected = text.replace("y = -0.0 # keep this note", "y = 3.25 # keep this note")
    assert plan["drafts"] == [
        {
            "path": source.path,
            "expected_source_revision": revision,
            "expected_sha256": sha256hash(text),
            "text": expected,
            "sha256": sha256hash(expected),
            "source_revision": f"sha256:{sha256hash(expected)}",
        }
    ]
    assert plan["source_replacements"][0]["expected"] == "-0.0"
    assert plan["source_replacements"][0]["replacement"] == "3.25"
    assert plan == plan_technology_diagram_edits(
        [source],
        position_intents=[
            {
                "technology_id": "TECH_A",
                "x": 1.0,
                "y": 3.25,
                "source_revision": revision,
            }
        ],
    )


def test_edge_plan_adds_and_removes_exact_owner_source_without_metadata_or_legacy() -> None:
    root = TechnologySource("modules/technology/root/def.txt", _technology_source("ROOT", x="0", y="0"))
    source_a = TechnologySource(
        "modules/technology/a/def.txt",
        _technology_source(
            '"TECH A"',
            x="1",
            y="1",
            extra=(
                "        dependencies = {\n"
                "            ROOT = 1\n"
                "        }\n"
                "        path = {\n"
                '            leads_to_tech = "TECH B"\n'
                "            research_cost_coeff = 1\n"
                "        }\n"
            ),
        ),
    )
    source_b = TechnologySource("modules/technology/b/def.txt", _technology_source('"TECH B"', x="2", y="2"))
    sources = [source_a, root, source_b]
    nodes = {row["id"]: row for row in technology_diagram_projection(sources)["nodes"]}
    intents = [
        TechnologyEdgeIntent("dependency", "ROOT", "TECH A", False, nodes["TECH A"]["source_revision"]),
        TechnologyEdgeIntent("path", "TECH A", "TECH B", False, nodes["TECH A"]["source_revision"]),
        TechnologyEdgeIntent("dependency", "TECH A", "TECH B", True, nodes["TECH B"]["source_revision"]),
        TechnologyEdgeIntent("path", "TECH B", "ROOT", True, nodes["TECH B"]["source_revision"]),
    ]

    plan = plan_technology_diagram_edits(sources, edge_intents=intents)

    assert plan["status"] == "planned"
    assert plan["diagnostics"] == []
    assert plan["summary"] == {
        "position_intent_count": 0,
        "edge_intent_count": 4,
        "replacement_count": 3,
        "draft_count": 2,
        "diagnostic_count": 0,
    }
    drafts = {row["path"]: row["text"] for row in plan["drafts"]}
    assert drafts[source_a.path] == _technology_source(
        '"TECH A"',
        x="1",
        y="1",
        extra=("        dependencies = {\n" "        }\n"),
    )
    assert drafts[source_b.path] == _insert_before_technology_close(
        source_b.text,
        (
            "        dependencies = {\n"
            '            "TECH A" = 1\n'
            "        }\n"
            "        path = {\n"
            "            leads_to_tech = ROOT\n"
            "            research_cost_coeff = 1\n"
            "        }\n"
        ),
    )
    assert all("meta" not in row["path"] and "legacy" not in row["path"] for row in plan["drafts"])
    edited_projection = technology_diagram_projection(
        [
            root,
            TechnologySource(source_a.path, drafts[source_a.path]),
            TechnologySource(source_b.path, drafts[source_b.path]),
        ]
    )
    assert {(row["kind"], row["source"], row["target"]) for row in edited_projection["edges"]} == {
        ("dependency", "TECH A", "TECH B"),
        ("path", "TECH B", "ROOT"),
    }
    assert plan == plan_technology_diagram_edits(list(reversed(sources)), edge_intents=list(reversed(intents)))


def test_plan_is_atomic_when_one_review_revision_is_stale() -> None:
    source_a = TechnologySource("modules/technology/a/def.txt", _technology_source("TECH_A", x="1", y="1"))
    source_b = TechnologySource("modules/technology/b/def.txt", _technology_source("TECH_B", x="2", y="2"))
    sources = [source_a, source_b]
    nodes = {row["id"]: row for row in technology_diagram_projection(sources)["nodes"]}

    plan = plan_technology_diagram_edits(
        sources,
        position_intents=[
            TechnologyPositionIntent("TECH_A", 8, 9, nodes["TECH_A"]["source_revision"]),
        ],
        edge_intents=[
            TechnologyEdgeIntent("path", "TECH_B", "TECH_A", True, f"sha256:{'0' * 64}"),
        ],
    )

    assert plan["status"] == "blocked"
    assert plan["drafts"] == []
    assert plan["source_replacements"] == []
    assert plan["summary"]["draft_count"] == 0
    assert plan["summary"]["replacement_count"] == 0
    assert [row["code"] for row in plan["diagnostics"]] == [
        "technology.plan.source_revision_mismatch",
    ]


def test_path_plan_reuses_one_empty_pihc3_placeholder_in_place() -> None:
    source_a = TechnologySource(
        "modules/technology/a/def.txt",
        _technology_source(
            "TECH_A",
            x="1",
            y="1",
            extra=("        path = {\n" "        }\n"),
        ),
    )
    source_b = TechnologySource("modules/technology/b/def.txt", _technology_source("TECH_B", x="2", y="2"))
    sources = [source_a, source_b]
    projection = technology_diagram_projection(sources)
    nodes = {row["id"]: row for row in projection["nodes"]}

    plan = plan_technology_diagram_edits(
        sources,
        edge_intents=[
            TechnologyEdgeIntent("path", "TECH_A", "TECH_B", True, nodes["TECH_A"]["source_revision"]),
        ],
    )

    assert projection["diagnostics"] == []
    assert plan["status"] == "planned"
    assert plan["summary"]["replacement_count"] == 1
    text = plan["drafts"][0]["text"]
    assert text.count("        path = {") == 1
    assert ("        path = {\n" "            leads_to_tech = TECH_B\n" "            research_cost_coeff = 1\n" "        }\n") in text
    edited = technology_diagram_projection(
        [
            TechnologySource(source_a.path, text),
            source_b,
        ]
    )
    assert [(row["kind"], row["source"], row["target"]) for row in edited["edges"]] == [
        ("path", "TECH_A", "TECH_B"),
    ]


def test_plan_can_remove_a_reviewed_dangling_edge_but_cannot_invent_one() -> None:
    source = TechnologySource(
        "modules/technology/a/def.txt",
        _technology_source(
            "TECH_A",
            x="1",
            y="1",
            extra=("        path = {\n" "            leads_to_tech = MISSING_TECH\n" "            research_cost_coeff = 1\n" "        }\n"),
        ),
    )
    projection = technology_diagram_projection([source])
    revision = projection["nodes"][0]["source_revision"]

    removal = plan_technology_diagram_edits(
        [source],
        edge_intents=[
            TechnologyEdgeIntent("path", "TECH_A", "MISSING_TECH", False, revision),
        ],
    )
    addition = plan_technology_diagram_edits(
        [source],
        edge_intents=[
            TechnologyEdgeIntent("path", "TECH_A", "ANOTHER_MISSING_TECH", True, revision),
        ],
    )

    assert [row["code"] for row in projection["diagnostics"]] == [
        "technology.edge.unresolved",
    ]
    assert removal["status"] == "planned"
    assert removal["summary"]["replacement_count"] == 1
    assert "MISSING_TECH" not in removal["drafts"][0]["text"]
    assert addition["status"] == "blocked"
    assert addition["drafts"] == []
    assert [row["code"] for row in addition["diagnostics"]] == [
        "technology.plan.edge_node_unresolved",
        "technology.edge.unresolved",
    ]


def test_comment_owned_removals_and_insertions_fail_closed() -> None:
    source_a = TechnologySource(
        "modules/technology/a/def.txt",
        _technology_source(
            "TECH_A",
            x="1",
            y="1",
            extra=(
                "        path = {\n"
                "            # This explanation belongs to the path.\n"
                "            leads_to_tech = TECH_B\n"
                "            research_cost_coeff = 1\n"
                "        }\n"
            ),
        ),
    )
    source_b = TechnologySource(
        "modules/technology/b/def.txt",
        _insert_before_technology_close(
            _technology_source("TECH_B", x="2", y="2"),
            "        # Keep this footer next to the technology close.\n",
        ),
    )
    sources = [source_a, source_b]
    nodes = {row["id"]: row for row in technology_diagram_projection(sources)["nodes"]}

    removal = plan_technology_diagram_edits(
        sources,
        edge_intents=[
            TechnologyEdgeIntent("path", "TECH_A", "TECH_B", False, nodes["TECH_A"]["source_revision"]),
        ],
    )
    insertion = plan_technology_diagram_edits(
        sources,
        edge_intents=[
            TechnologyEdgeIntent("dependency", "TECH_A", "TECH_B", True, nodes["TECH_B"]["source_revision"]),
        ],
    )

    assert removal["status"] == "blocked"
    assert removal["drafts"] == []
    assert [row["code"] for row in removal["diagnostics"]] == [
        "technology.plan.path_unsafe",
    ]
    assert "owns comments" in removal["diagnostics"][0]["message"]
    assert insertion["status"] == "blocked"
    assert insertion["drafts"] == []
    assert [row["code"] for row in insertion["diagnostics"]] == [
        "technology.plan.dependency_unsafe",
    ]
    assert "trailing comments" in insertion["diagnostics"][0]["message"]


def test_projection_and_plan_reject_ambiguous_or_malformed_inputs_without_crashing() -> None:
    duplicate_a = TechnologySource("modules/technology/a/def.txt", _technology_source("DUPLICATE", x="0", y="0"))
    duplicate_b = TechnologySource("modules/technology/b/def.txt", _technology_source("DUPLICATE", x="1", y="1"))
    duplicate_projection = technology_diagram_projection([duplicate_b, duplicate_a])

    assert duplicate_projection["editable"] is False
    assert [row["code"] for row in duplicate_projection["diagnostics"]] == [
        "technology.node.duplicate_id",
    ]
    assert all(row["editable"] is False for row in duplicate_projection["nodes"])
    duplicate_plan = plan_technology_diagram_edits(
        [duplicate_a, duplicate_b],
        position_intents=[
            TechnologyPositionIntent(
                "DUPLICATE",
                5,
                6,
                duplicate_projection["nodes"][0]["source_revision"],
            )
        ],
    )
    assert duplicate_plan["status"] == "blocked"
    assert duplicate_plan["drafts"] == []
    assert {row["code"] for row in duplicate_plan["diagnostics"]} == {
        "technology.node.duplicate_id",
        "technology.plan.node_unresolved",
    }

    malformed_projection = technology_diagram_projection(
        [
            TechnologySource(None, "technologies = {}"),  # type: ignore[arg-type]
            {"path": "modules/technology/bad/def.txt", "text": "technologies = {"},
            {"path": "modules/technology/unicode/def.txt", "text": "\ud800"},
        ]
    )
    assert malformed_projection["editable"] is False
    assert malformed_projection["nodes"] == []
    assert {row["code"] for row in malformed_projection["diagnostics"]} == {
        "pdx.unclosed_block",
        "technology.source.invalid_record",
        "technology.source.invalid_unicode",
    }
    dumps_json(malformed_projection, ensure_ascii=False, sort_keys=True)

    valid = TechnologySource("modules/technology/valid/def.txt", _technology_source("VALID", x="0", y="0"))
    revision = technology_diagram_projection([valid])["nodes"][0]["source_revision"]
    invalid_intent = plan_technology_diagram_edits(
        [valid],
        edge_intents=[
            {
                "kind": [],
                "source_id": "VALID",
                "target_id": "OTHER",
                "present": True,
                "source_revision": revision,
            }
        ],
    )
    assert invalid_intent["status"] == "blocked"
    assert [row["code"] for row in invalid_intent["diagnostics"]] == [
        "technology.plan.invalid_edge_intent",
    ]
    assert technology_diagram_projection([])["editable"] is False


def test_position_plan_uses_plain_decimal_pdx_for_extreme_finite_coordinates() -> None:
    source = TechnologySource("modules/technology/a/def.txt", _technology_source("TECH_A", x="0", y="0"))
    revision = technology_diagram_projection([source])["nodes"][0]["source_revision"]

    plan = plan_technology_diagram_edits(
        [source],
        position_intents=[
            TechnologyPositionIntent(
                "TECH_A",
                1e-20,
                1e20,
                revision,
            )
        ],
    )

    assert plan["status"] == "planned"
    text = plan["drafts"][0]["text"]
    assert "x = 0.00000000000000000001" in text
    assert "y = 100000000000000000000" in text
    assert "e-" not in text
    assert "e+" not in text
    projected = technology_diagram_projection([TechnologySource(source.path, text)])
    assert projected["nodes"][0]["x"] == 1e-20
    assert projected["nodes"][0]["y"] == 100000000000000000000


def _technology_source(
    technology_literal: str,
    *,
    x: str,
    y: str,
    extra: str = "",
) -> str:
    return (
        "technologies = {\n"
        f"    {technology_literal} = {{\n"
        "        folder = {\n"
        "            name = industry_folder\n"
        "            position = {\n"
        f"                x = {x}\n"
        f"                y = {y}\n"
        "            }\n"
        "        }\n"
        f"{extra}"
        "        research_cost = 1\n"
        "    }\n"
        "}\n"
    )


def _insert_before_technology_close(text: str, insertion: str) -> str:
    suffix = "    }\n}\n"
    assert text.endswith(suffix)
    return text[: -len(suffix)] + insertion + suffix
