from __future__ import annotations

from heavenbase.utils import (
    dumps_json,
    enum_files,
    get_file_basename,
    load_bin,
    pj,
    sha256hash,
)

from paradev.games.hoi4.focus_tree import (
    FOCUS_TREE_DIAGRAM_PLAN_SCHEMA,
    FOCUS_TREE_DIAGRAM_PROJECTION_SCHEMA,
    FOCUS_TREE_NODE_CREATION_PLAN_SCHEMA,
    FocusCreationIntent,
    FocusEdgeIntent,
    FocusPositionIntent,
    FocusTreeLocalizationSource,
    FocusTreeSource,
    focus_tree_diagram_projection,
    plan_focus_tree_diagram_edits,
    plan_focus_tree_node_creation,
)


def test_focus_tree_projection_reads_containers_positions_icons_and_relations() -> None:
    alpha = FocusTreeSource(
        "modules/focus_tree/alpha/def.txt",
        _tree_source(
            "ALPHA_TREE",
            (
                _focus_source("FOCUS_A", x="0", y="0"),
                _focus_source(
                    "FOCUS_B",
                    x="1",
                    y="2",
                    extra=(
                        "        prerequisite = {\n"
                        "            focus = FOCUS_A\n"
                        "        }\n"
                        "        mutually_exclusive = {\n"
                        "            focus = FOCUS_C\n"
                        "        }\n"
                    ),
                ),
                _focus_source(
                    "FOCUS_C",
                    x="3",
                    y="4",
                    extra=("        mutually_exclusive = {\n" "            focus = FOCUS_B\n" "        }\n"),
                ),
            ),
        ),
    )
    beta = {
        "path": "modules/focus_tree/beta/def.txt",
        "text": _tree_source(
            "BETA_TREE",
            (_focus_source("FOCUS_D", x="8", y="9"),),
        ),
    }

    projection = focus_tree_diagram_projection([beta, alpha])

    assert projection["schema"] == FOCUS_TREE_DIAGRAM_PROJECTION_SCHEMA
    assert projection["source_kind"] == "module_def_pdx"
    assert projection["editable"] is True
    assert projection["summary"] == {
        "source_count": 2,
        "tree_count": 2,
        "node_count": 4,
        "edge_count": 2,
        "edge_counts": {"mutually_exclusive": 1, "prerequisite": 1},
        "relation_declaration_count": 3,
        "diagnostic_count": 0,
    }
    assert [row["id"] for row in projection["trees"]] == [
        "ALPHA_TREE",
        "BETA_TREE",
    ]
    assert [(row["id"], row["tree_id"], row["x"], row["y"], row["icon"]) for row in projection["nodes"]] == [
        ("FOCUS_A", "ALPHA_TREE", 0, 0, "GFX_FOCUS_A_icon"),
        ("FOCUS_B", "ALPHA_TREE", 1, 2, "GFX_FOCUS_B_icon"),
        ("FOCUS_C", "ALPHA_TREE", 3, 4, "GFX_FOCUS_C_icon"),
        ("FOCUS_D", "BETA_TREE", 8, 9, "GFX_FOCUS_D_icon"),
    ]
    assert [
        (
            row["kind"],
            row["source"],
            row["target"],
            row["declaration_count"],
        )
        for row in projection["edges"]
    ] == [
        ("mutually_exclusive", "FOCUS_B", "FOCUS_C", 2),
        ("prerequisite", "FOCUS_A", "FOCUS_B", 1),
    ]
    assert projection == focus_tree_diagram_projection([alpha, beta])
    dumps_json(projection, ensure_ascii=False, sort_keys=True)


def test_focus_position_plan_preserves_bom_crlf_comments_and_numeric_spelling() -> None:
    text = "\ufeff" + _tree_source(
        "TEST_TREE",
        (
            _focus_source(
                "FOCUS_A",
                x="1.000",
                y="-0.0 # keep this note",
            ),
        ),
    ).replace("\n", "\r\n")
    source = FocusTreeSource("modules/focus_tree/test/def.txt", text)
    projection = focus_tree_diagram_projection([source])
    revision = projection["nodes"][0]["source_revision"]

    plan = plan_focus_tree_diagram_edits(
        [source],
        position_intents=[
            FocusPositionIntent(
                focus_id="FOCUS_A",
                x=1.0,
                y=3.25,
                source_revision=revision,
            )
        ],
    )

    assert plan["schema"] == FOCUS_TREE_DIAGRAM_PLAN_SCHEMA
    assert plan["projection_schema"] == FOCUS_TREE_DIAGRAM_PROJECTION_SCHEMA
    assert plan["status"] == "planned"
    assert plan["offset_unit"] == "unicode_codepoint"
    assert plan["summary"] == {
        "position_intent_count": 1,
        "edge_intent_count": 0,
        "replacement_count": 1,
        "draft_count": 1,
        "diagnostic_count": 0,
    }
    expected = text.replace(
        "y = -0.0 # keep this note",
        "y = 3.25 # keep this note",
    )
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


def test_relation_plan_updates_exact_source_and_keeps_mutex_reciprocal() -> None:
    source = FocusTreeSource(
        "modules/focus_tree/test/def.txt",
        _tree_source(
            "TEST_TREE",
            (
                _focus_source("FOCUS_A", x="0", y="0"),
                _focus_source(
                    "FOCUS_B",
                    x="1",
                    y="1",
                    extra=("        prerequisite = {\n" "            focus = FOCUS_A\n" "        }\n"),
                ),
                _focus_source('"FOCUS C"', x="2", y="2"),
            ),
        ),
    )
    projection = focus_tree_diagram_projection([source])
    nodes = {row["id"]: row for row in projection["nodes"]}
    revision = nodes["FOCUS_A"]["source_revision"]
    intents = [
        FocusEdgeIntent(
            "prerequisite",
            "FOCUS_A",
            "FOCUS_B",
            False,
            revision,
        ),
        FocusEdgeIntent(
            "prerequisite",
            "FOCUS_A",
            "FOCUS C",
            True,
            revision,
        ),
        FocusEdgeIntent(
            "mutually_exclusive",
            "FOCUS_B",
            "FOCUS C",
            True,
            revision,
        ),
    ]

    plan = plan_focus_tree_diagram_edits(
        [source],
        edge_intents=intents,
    )

    assert plan["status"] == "planned"
    assert plan["diagnostics"] == []
    assert plan["summary"]["draft_count"] == 1
    assert plan["summary"]["replacement_count"] == 3
    draft = plan["drafts"][0]["text"]
    assert "focus = FOCUS_A" in draft
    assert draft.count('focus = "FOCUS C"') == 1
    assert draft.count("focus = FOCUS_B") == 1
    assert all("meta" not in row["path"] and "legacy" not in row["path"] for row in plan["drafts"])
    edited = focus_tree_diagram_projection([FocusTreeSource(source.path, draft)])
    assert {(row["kind"], row["source"], row["target"]) for row in edited["edges"]} == {
        ("prerequisite", "FOCUS_A", "FOCUS C"),
        ("mutually_exclusive", "FOCUS C", "FOCUS_B"),
    }
    mutex = next(row for row in edited["edges"] if row["kind"] == "mutually_exclusive")
    assert mutex["declaration_count"] == 2
    assert plan == plan_focus_tree_diagram_edits(
        [source],
        edge_intents=list(reversed(intents)),
    )


def test_prerequisite_addition_fails_closed_when_or_group_is_ambiguous() -> None:
    source = FocusTreeSource(
        "modules/focus_tree/test/def.txt",
        _tree_source(
            "TEST_TREE",
            (
                _focus_source("FOCUS_A", x="0", y="0"),
                _focus_source("FOCUS_C", x="1", y="0"),
                _focus_source("FOCUS_D", x="2", y="0"),
                _focus_source(
                    "FOCUS_B",
                    x="1",
                    y="1",
                    extra=(
                        "        prerequisite = {\n"
                        "            focus = FOCUS_A\n"
                        "        }\n"
                        "        prerequisite = {\n"
                        "            focus = FOCUS_C\n"
                        "        }\n"
                    ),
                ),
            ),
        ),
    )
    projection = focus_tree_diagram_projection([source])
    revision = next(row["source_revision"] for row in projection["nodes"] if row["id"] == "FOCUS_B")

    addition = plan_focus_tree_diagram_edits(
        [source],
        edge_intents=[
            FocusEdgeIntent(
                "prerequisite",
                "FOCUS_D",
                "FOCUS_B",
                True,
                revision,
            )
        ],
    )
    removal = plan_focus_tree_diagram_edits(
        [source],
        edge_intents=[
            FocusEdgeIntent(
                "prerequisite",
                "FOCUS_A",
                "FOCUS_B",
                False,
                revision,
            )
        ],
    )

    assert addition["status"] == "blocked"
    assert addition["drafts"] == []
    assert [row["code"] for row in addition["diagnostics"]] == [
        "focus_tree.plan.prerequisite_unsafe",
    ]
    assert "multiple prerequisite groups" in addition["diagnostics"][0]["message"]
    assert removal["status"] == "planned"
    assert "focus = FOCUS_A" not in removal["drafts"][0]["text"]
    assert "focus = FOCUS_C" in removal["drafts"][0]["text"]


def test_focus_plan_is_atomic_for_stale_revisions_and_comment_owned_relations() -> None:
    source = FocusTreeSource(
        "modules/focus_tree/test/def.txt",
        _tree_source(
            "TEST_TREE",
            (
                _focus_source("FOCUS_A", x="0", y="0"),
                _focus_source(
                    "FOCUS_B",
                    x="1",
                    y="1",
                    extra=("        prerequisite = {\n" "            # Keep this authored explanation.\n" "            focus = FOCUS_A\n" "        }\n"),
                ),
            ),
        ),
    )
    projection = focus_tree_diagram_projection([source])
    nodes = {row["id"]: row for row in projection["nodes"]}
    stale = f"sha256:{'0' * 64}"

    stale_plan = plan_focus_tree_diagram_edits(
        [source],
        position_intents=[
            FocusPositionIntent(
                "FOCUS_A",
                8,
                9,
                nodes["FOCUS_A"]["source_revision"],
            )
        ],
        edge_intents=[
            FocusEdgeIntent(
                "prerequisite",
                "FOCUS_A",
                "FOCUS_B",
                False,
                stale,
            )
        ],
    )
    comment_plan = plan_focus_tree_diagram_edits(
        [source],
        edge_intents=[
            FocusEdgeIntent(
                "prerequisite",
                "FOCUS_A",
                "FOCUS_B",
                False,
                nodes["FOCUS_B"]["source_revision"],
            )
        ],
    )

    assert stale_plan["status"] == "blocked"
    assert stale_plan["drafts"] == []
    assert stale_plan["source_replacements"] == []
    assert [row["code"] for row in stale_plan["diagnostics"]] == [
        "focus_tree.plan.source_revision_mismatch",
    ]
    assert comment_plan["status"] == "blocked"
    assert comment_plan["drafts"] == []
    assert [row["code"] for row in comment_plan["diagnostics"]] == [
        "focus_tree.plan.prerequisite_unsafe",
    ]
    assert "owns comments" in comment_plan["diagnostics"][0]["message"]


def test_focus_node_creation_plans_exact_definition_localization_and_absent_image() -> None:
    def_text = _tree_source(
        "TEST_TREE",
        (_focus_source("FOCUS_A", x="0", y="0"),),
    )
    loc_text = "[en.FOCUS_A]\nExisting focus\n"
    def_source = FocusTreeSource(
        "src/modules/focus_tree/TEST_TREE/def.txt",
        def_text,
    )
    loc_source = FocusTreeLocalizationSource(
        "src/modules/focus_tree/TEST_TREE/main.loc",
        loc_text,
    )
    intent = FocusCreationIntent(
        tree_id="TEST_TREE",
        focus_id="FOCUS_NEW",
        x=2,
        y=3,
        title="A New Direction",
        description="First line.\nSecond line.",
        source_revision=f"sha256:{sha256hash(def_text)}",
        localization_source_revision=f"sha256:{sha256hash(loc_text)}",
        relative_position_id="FOCUS_A",
        prerequisite_id="FOCUS_A",
    )

    plan = plan_focus_tree_node_creation(
        [def_source],
        localization_sources=[loc_source],
        intent=intent,
        occupied_paths=[def_source.path, loc_source.path],
    )

    assert plan["schema"] == FOCUS_TREE_NODE_CREATION_PLAN_SCHEMA
    assert plan["projection_schema"] == FOCUS_TREE_DIAGRAM_PROJECTION_SCHEMA
    assert plan["status"] == "planned"
    assert plan["write"] is False
    assert plan["diagnostics"] == []
    assert plan["summary"] == {
        "focus_source_count": 1,
        "localization_source_count": 1,
        "replacement_count": 2,
        "draft_count": 2,
        "absent_file_target_count": 1,
        "diagnostic_count": 0,
    }
    assert plan["absent_file_targets"] == [
        {
            "path": "src/modules/focus_tree/TEST_TREE/icons/FOCUS_NEW.png",
            "kind": "focus_preview_png",
            "content_type": "image/png",
            "precondition": "absent",
            "write": False,
        }
    ]
    drafts = {row["path"]: row for row in plan["drafts"]}
    def_draft = drafts[def_source.path]
    loc_draft = drafts[loc_source.path]
    assert def_draft["expected_source_revision"] == intent.source_revision
    assert loc_draft["expected_source_revision"] == intent.localization_source_revision
    assert (
        "    focus = {\n"
        "        id = FOCUS_NEW\n"
        "        icon = GFX_goal_unknown\n"
        "        relative_position_id = FOCUS_A\n"
        "        prerequisite = {\n"
        "            focus = FOCUS_A\n"
        "        }\n"
        "        x = 2\n"
        "        y = 3\n"
        "    }\n"
    ) in def_draft["text"]
    assert loc_draft["text"].endswith("\n[en.FOCUS_NEW]\n" "A New Direction\n\n" "[en.FOCUS_NEW_desc]\n" "First line.\n" "Second line.\n")
    projected = focus_tree_diagram_projection([FocusTreeSource(def_source.path, def_draft["text"])])
    assert next(row for row in projected["nodes"] if row["id"] == "FOCUS_NEW") == {
        "id": "FOCUS_NEW",
        "tree_id": "TEST_TREE",
        "x": 2,
        "y": 3,
        "source_path": def_source.path,
        "source_revision": def_draft["source_revision"],
        "editable": True,
        "icon": "GFX_goal_unknown",
        "relative_position_id": "FOCUS_A",
        "source_span": {"line": 10, "column": 14},
    }
    assert ("prerequisite", "FOCUS_A", "FOCUS_NEW") in {(row["kind"], row["source"], row["target"]) for row in projected["edges"]}
    assert plan == plan_focus_tree_node_creation(
        [def_source],
        localization_sources=[loc_source],
        intent=intent,
        occupied_paths=[loc_source.path, def_source.path],
    )
    dumps_json(plan, ensure_ascii=False, sort_keys=True)


def test_focus_node_creation_never_overwrites_ids_localization_or_images() -> None:
    def_text = _tree_source(
        "TEST_TREE",
        (_focus_source("FOCUS_EXISTING", x="0", y="0"),),
    )
    loc_text = "[en.FOCUS_EXISTING]\nExisting focus\n\n" "[english.FOCUS_RESERVED]\nReserved title\n"
    def_source = FocusTreeSource(
        "src/modules/focus_tree/TEST_TREE/def.txt",
        def_text,
    )
    loc_source = FocusTreeLocalizationSource(
        "src/modules/focus_tree/TEST_TREE/main.loc",
        loc_text,
    )

    def plan(focus_id: str, *, occupied_paths: list[str]) -> dict[str, object]:
        return plan_focus_tree_node_creation(
            [def_source],
            localization_sources=[loc_source],
            intent=FocusCreationIntent(
                tree_id="TEST_TREE",
                focus_id=focus_id,
                x=1,
                y=1,
                title="Title",
                description="Description",
                source_revision=f"sha256:{sha256hash(def_text)}",
                localization_source_revision=f"sha256:{sha256hash(loc_text)}",
            ),
            occupied_paths=occupied_paths,
        )

    duplicate_id = plan("FOCUS_EXISTING", occupied_paths=[])
    portable_duplicate_id = plan("focus_existing", occupied_paths=[])
    duplicate_loc = plan("FOCUS_RESERVED", occupied_paths=[])
    occupied_image = plan(
        "FOCUS_NEW",
        occupied_paths=[
            "src/modules/focus_tree/TEST_TREE/icons/focus_new.PNG",
        ],
    )

    assert [row["code"] for row in duplicate_id["diagnostics"]] == [
        "focus_tree.create.focus_id_exists",
        "focus_tree.create.localization_key_exists",
    ]
    assert [row["code"] for row in duplicate_loc["diagnostics"]] == [
        "focus_tree.create.localization_key_exists",
    ]
    assert [row["code"] for row in portable_duplicate_id["diagnostics"]] == [
        "focus_tree.create.focus_id_portable_collision",
    ]
    assert [row["code"] for row in occupied_image["diagnostics"]] == [
        "focus_tree.create.image_target_exists",
    ]
    for blocked in (
        duplicate_id,
        portable_duplicate_id,
        duplicate_loc,
        occupied_image,
    ):
        assert blocked["status"] == "blocked"
        assert blocked["drafts"] == []
        assert blocked["source_replacements"] == []
        assert blocked["absent_file_targets"] == []


def test_focus_node_creation_rejects_unicode_localization_line_separators() -> None:
    def_text = _tree_source(
        "TEST_TREE",
        (_focus_source("FOCUS_EXISTING", x="0", y="0"),),
    )
    loc_text = "[en.FOCUS_EXISTING]\nExisting focus\n"
    def_source = FocusTreeSource(
        "src/modules/focus_tree/TEST_TREE/def.txt",
        def_text,
    )
    loc_source = FocusTreeLocalizationSource(
        "src/modules/focus_tree/TEST_TREE/main.loc",
        loc_text,
    )

    def plan(*, title: str, description: str) -> dict[str, object]:
        return plan_focus_tree_node_creation(
            [def_source],
            localization_sources=[loc_source],
            intent=FocusCreationIntent(
                tree_id="TEST_TREE",
                focus_id="FOCUS_NEW",
                x=1,
                y=1,
                title=title,
                description=description,
                source_revision=f"sha256:{sha256hash(def_text)}",
                localization_source_revision=f"sha256:{sha256hash(loc_text)}",
            ),
            occupied_paths=[],
        )

    for separator in ("\x85", "\u2028", "\u2029"):
        injected_title = plan(
            title=f"Title{separator}[en.INJECTED_KEY]",
            description="Description",
        )
        injected_description = plan(
            title="Title",
            description=(f"Description{separator}[en.INJECTED_KEY]" f"{separator}Injected"),
        )

        assert [row["code"] for row in injected_title["diagnostics"]] == [
            "focus_tree.create.invalid_title",
        ]
        assert [row["code"] for row in injected_description["diagnostics"]] == [
            "focus_tree.create.invalid_description",
        ]
        for blocked in (injected_title, injected_description):
            assert blocked["status"] == "blocked"
            assert blocked["drafts"] == []
            assert blocked["source_replacements"] == []


def test_focus_node_creation_fails_closed_for_stale_ambiguous_or_unsafe_sources() -> None:
    def_text = _tree_source(
        "TEST_TREE",
        (_focus_source("FOCUS_A", x="0", y="0"),),
    ) + _tree_source(
        "OTHER_TREE",
        (_focus_source("FOCUS_B", x="0", y="0"),),
    )
    loc_text = "[en.FOCUS_A]\nExisting focus\n"
    intent = {
        "tree_id": "TEST_TREE",
        "focus_id": "FOCUS_NEW",
        "x": 1,
        "y": 2,
        "title": "Title",
        "description": "[Root.GetName]",
        "source_revision": f"sha256:{'0' * 64}",
        "localization_source_revision": f"sha256:{sha256hash(loc_text)}",
    }

    plan = plan_focus_tree_node_creation(
        [
            FocusTreeSource(
                "src/modules/focus_tree/TEST_TREE/def.txt",
                def_text,
            )
        ],
        localization_sources=[
            FocusTreeLocalizationSource(
                "src/modules/focus_tree/TEST_TREE/main.loc",
                loc_text,
            )
        ],
        intent=intent,
        occupied_paths=[],
    )

    assert plan["status"] == "blocked"
    assert plan["intent"] is None
    assert plan["drafts"] == []
    assert [row["code"] for row in plan["diagnostics"]] == [
        "focus_tree.create.invalid_description",
    ]

    intent["description"] = "Safe description"
    ambiguous = plan_focus_tree_node_creation(
        [
            FocusTreeSource(
                "src/modules/focus_tree/TEST_TREE/def.txt",
                def_text,
            )
        ],
        localization_sources=[
            FocusTreeLocalizationSource(
                "src/modules/focus_tree/TEST_TREE/main.loc",
                loc_text,
            )
        ],
        intent=intent,
        occupied_paths=[],
    )
    assert ambiguous["status"] == "blocked"
    assert ambiguous["drafts"] == []
    assert [row["code"] for row in ambiguous["diagnostics"]] == [
        "focus_tree.create.source_ambiguous",
    ]


def test_focus_projection_rejects_malformed_duplicate_and_unbounded_inputs() -> None:
    duplicate_a = FocusTreeSource(
        "modules/focus_tree/a/def.txt",
        _tree_source(
            "TREE_A",
            (_focus_source("DUPLICATE", x="0", y="0"),),
        ),
    )
    duplicate_b = FocusTreeSource(
        "modules/focus_tree/b/def.txt",
        _tree_source(
            "TREE_B",
            (_focus_source("DUPLICATE", x="1", y="1"),),
        ),
    )
    duplicate = focus_tree_diagram_projection([duplicate_b, duplicate_a])

    assert duplicate["editable"] is False
    assert [row["code"] for row in duplicate["diagnostics"]] == [
        "focus_tree.focus.duplicate_id",
    ]
    assert all(row["editable"] is False for row in duplicate["nodes"])

    malformed = focus_tree_diagram_projection(
        [
            FocusTreeSource(None, "focus_tree = {}"),  # type: ignore[arg-type]
            {
                "path": "modules/focus_tree/bad/def.txt",
                "text": "focus_tree = {",
            },
            {
                "path": "modules/focus_tree/unicode/def.txt",
                "text": "\ud800",
            },
        ]
    )
    assert malformed["editable"] is False
    assert malformed["nodes"] == []
    assert {row["code"] for row in malformed["diagnostics"]} == {
        "focus_tree.source.invalid_record",
        "focus_tree.source.invalid_unicode",
        "pdx.unclosed_block",
    }

    too_many = focus_tree_diagram_projection(
        [
            FocusTreeSource(
                f"modules/focus_tree/{index}/def.txt",
                "",
            )
            for index in range(257)
        ]
    )
    assert too_many["sources"] == []
    assert [row["code"] for row in too_many["diagnostics"]] == [
        "focus_tree.source.limit_exceeded",
    ]


def test_pihc3_focus_tree_projection_covers_all_authoritative_containers() -> None:
    from paradev.sdk import Project

    project = Project.load(pj("projects", "PIHC3", abs=True))
    projection = project.module_diagram("focus")

    assert projection["editable"] is True
    assert projection["diagnostics"] == []
    assert projection["summary"] == {
        "source_count": 28,
        "tree_count": 28,
        "node_count": 738,
        "edge_count": 863,
        "edge_counts": {
            "mutually_exclusive": 23,
            "prerequisite": 840,
        },
        "relation_declaration_count": 886,
        "diagnostic_count": 0,
    }
    assert all(row["source_path"].endswith("/def.txt") for row in projection["nodes"])
    assert all(row["editable"] is True for row in projection["nodes"])

    node = next(row for row in projection["nodes"] if row["id"] == "FOCUS_C01_CANTERLOT_PACT")
    plan = project.edit_module_diagram(
        "focus",
        position_intents=[
            {
                "focus_id": "FOCUS_C01_CANTERLOT_PACT",
                "x": 20,
                "y": 0,
                "source_revision": node["source_revision"],
            }
        ],
    )
    assert plan["status"] == "planned"
    assert plan["diagnostics"] == []
    assert plan["summary"]["draft_count"] == 1
    assert plan["drafts"][0]["path"] == ("src/modules/focus/" "FOCUS_C01_CANTERLOT_PACT - 《坎特洛特协定》/def.txt")
    assert "\tx = 20\n" in plan["drafts"][0]["text"]


def _tree_source(
    tree_id: str,
    focuses: tuple[str, ...],
) -> str:
    return "focus_tree = {\n" f"    id = {tree_id}\n" f"{''.join(focuses)}" "}\n"


def _focus_source(
    focus_literal: str,
    *,
    x: str,
    y: str,
    extra: str = "",
) -> str:
    focus_id = focus_literal.strip('"')
    return (
        "    focus = {\n"
        f"        id = {focus_literal}\n"
        f"        icon = GFX_{focus_id}_icon\n"
        f"{extra}"
        f"        x = {x}\n"
        f"        y = {y}\n"
        "    }\n"
    )
