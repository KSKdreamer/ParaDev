from __future__ import annotations

from heavenbase.utils import dumps_yaml

from paradev.games.hoi4.doctrine import (
    DOCTRINE_DIAGRAM_PLAN_SCHEMA,
    DOCTRINE_DIAGRAM_PROJECTION_SCHEMA,
    DOCTRINE_DIAGRAM_STATE_SCHEMA,
    doctrine_diagram_projection,
    plan_doctrine_diagram_edits,
)


def _state(
    *,
    x: int,
    y: int,
    paths: tuple[str, ...] = (),
    mutually_exclusive: tuple[str, ...] = (),
) -> str:
    return dumps_yaml(
        {
            "schema": DOCTRINE_DIAGRAM_STATE_SCHEMA,
            "position": {"x": x, "y": y},
            "paths": list(paths),
            "mutually_exclusive": list(mutually_exclusive),
        },
        sort_keys=False,
    )


def _source(
    doctrine_id: str,
    compiled_id: str,
    *,
    x: int,
    y: int,
    paths: tuple[str, ...] = (),
    mutually_exclusive: tuple[str, ...] = (),
) -> dict[str, object]:
    root = f"src/modules/doctrine/{doctrine_id}"
    return {
        "object_id": doctrine_id,
        "module_id": f"doctrine/{doctrine_id}",
        "definition_path": f"{root}/def.txt",
        "definition_text": f"{compiled_id} = {{\n\txp_cost = 100\n}}\n",
        "diagram_path": f"{root}/.paradev/diagram.yaml",
        "diagram_text": _state(
            x=x,
            y=y,
            paths=paths,
            mutually_exclusive=mutually_exclusive,
        ),
    }


def test_doctrine_projection_uses_definition_identity_and_hidden_state() -> None:
    sources = [
        _source(
            "DOCTRINE_ROOT",
            "compiled_root",
            x=0,
            y=0,
            paths=("DOCTRINE_LEFT",),
            mutually_exclusive=("DOCTRINE_RIGHT",),
        ),
        _source(
            "DOCTRINE_LEFT",
            "compiled_left",
            x=-2,
            y=2,
        ),
        _source(
            "DOCTRINE_RIGHT",
            "compiled_right",
            x=2,
            y=2,
            mutually_exclusive=("DOCTRINE_ROOT",),
        ),
    ]

    projection = doctrine_diagram_projection(sources)

    assert projection["schema"] == DOCTRINE_DIAGRAM_PROJECTION_SCHEMA
    assert projection["editable"] is True
    assert projection["summary"] == {
        "source_count": 6,
        "definition_count": 3,
        "diagram_state_count": 3,
        "node_count": 3,
        "editable_node_count": 3,
        "edge_count": 2,
        "edge_counts": {"mutually_exclusive": 1, "path": 1},
        "diagnostic_count": 0,
    }
    nodes = {row["id"]: row for row in projection["nodes"]}
    assert nodes["DOCTRINE_ROOT"]["compiled_id"] == "compiled_root"
    assert (nodes["DOCTRINE_LEFT"]["x"], nodes["DOCTRINE_LEFT"]["y"]) == (
        -2,
        2,
    )
    assert {(row["kind"], row["source"], row["target"]) for row in projection["edges"]} == {
        ("path", "DOCTRINE_ROOT", "DOCTRINE_LEFT"),
        ("mutually_exclusive", "DOCTRINE_RIGHT", "DOCTRINE_ROOT"),
    }


def test_doctrine_plan_updates_positions_and_relationships_symmetrically() -> None:
    sources = [
        _source(
            "DOCTRINE_ROOT",
            "compiled_root",
            x=0,
            y=0,
            paths=("DOCTRINE_LEFT",),
        ),
        _source(
            "DOCTRINE_LEFT",
            "compiled_left",
            x=-2,
            y=2,
        ),
        _source(
            "DOCTRINE_RIGHT",
            "compiled_right",
            x=2,
            y=2,
        ),
    ]
    projection = doctrine_diagram_projection(sources)
    nodes = {row["id"]: row for row in projection["nodes"]}

    plan = plan_doctrine_diagram_edits(
        sources,
        position_intents=[
            {
                "doctrine_id": "DOCTRINE_LEFT",
                "x": -4,
                "y": 3,
                "source_revision": nodes["DOCTRINE_LEFT"]["source_revision"],
            }
        ],
        edge_intents=[
            {
                "kind": "path",
                "source_id": "DOCTRINE_ROOT",
                "target_id": "DOCTRINE_LEFT",
                "present": False,
                "source_revision": nodes["DOCTRINE_ROOT"]["source_revision"],
            },
            {
                "kind": "mutually_exclusive",
                "source_id": "DOCTRINE_LEFT",
                "target_id": "DOCTRINE_RIGHT",
                "present": True,
                "source_revision": nodes["DOCTRINE_LEFT"]["source_revision"],
            },
        ],
    )

    assert plan["schema"] == DOCTRINE_DIAGRAM_PLAN_SCHEMA
    assert plan["status"] == "planned"
    assert plan["summary"]["draft_count"] == 3
    drafts = {row["path"]: row["text"] for row in plan["drafts"]}
    assert "    x: -4\n    y: 3\n" in drafts["src/modules/doctrine/DOCTRINE_LEFT/.paradev/diagram.yaml"]
    assert "paths: []\n" in drafts["src/modules/doctrine/DOCTRINE_ROOT/.paradev/diagram.yaml"]
    assert "mutually_exclusive:\n- DOCTRINE_RIGHT\n" in drafts["src/modules/doctrine/DOCTRINE_LEFT/.paradev/diagram.yaml"]
    assert "mutually_exclusive:\n- DOCTRINE_LEFT\n" in drafts["src/modules/doctrine/DOCTRINE_RIGHT/.paradev/diagram.yaml"]


def test_doctrine_plan_blocks_missing_state_and_stale_revision() -> None:
    source = _source(
        "DOCTRINE_ROOT",
        "compiled_root",
        x=0,
        y=0,
    )
    projection = doctrine_diagram_projection([source])
    revision = projection["nodes"][0]["source_revision"]
    source["diagram_text"] = None

    missing = doctrine_diagram_projection([source])
    stale = plan_doctrine_diagram_edits(
        [
            _source(
                "DOCTRINE_ROOT",
                "compiled_root",
                x=9,
                y=0,
            )
        ],
        position_intents=[
            {
                "doctrine_id": "DOCTRINE_ROOT",
                "x": 1,
                "y": 1,
                "source_revision": revision,
            }
        ],
    )

    assert missing["editable"] is False
    assert missing["nodes"][0]["editable"] is False
    assert missing["diagnostics"][0]["code"] == "doctrine.state.missing"
    assert stale["status"] == "blocked"
    assert stale["drafts"] == []
    assert any(row["code"] == "doctrine.plan.source_revision_mismatch" for row in stale["diagnostics"])


def test_doctrine_plan_links_existing_parent_to_pending_child() -> None:
    source = _source(
        "DOCTRINE_ROOT",
        "compiled_root",
        x=0,
        y=0,
    )
    projection = doctrine_diagram_projection([source])
    revision = projection["nodes"][0]["source_revision"]

    plan = plan_doctrine_diagram_edits(
        [source],
        edge_intents=[
            {
                "kind": "path",
                "source_id": "DOCTRINE_ROOT",
                "target_id": "DOCTRINE_CHILD",
                "present": True,
                "source_revision": revision,
            }
        ],
        pending_node_ids=["DOCTRINE_CHILD"],
    )

    assert plan["status"] == "planned"
    assert plan["intents"]["pending_node_ids"] == ["DOCTRINE_CHILD"]
    assert plan["summary"]["draft_count"] == 1
    assert "paths:\n- DOCTRINE_CHILD\n" in plan["drafts"][0]["text"]


def test_doctrine_plan_rejects_unsupported_pending_relationships() -> None:
    source = _source(
        "DOCTRINE_ROOT",
        "compiled_root",
        x=0,
        y=0,
    )
    projection = doctrine_diagram_projection([source])
    revision = projection["nodes"][0]["source_revision"]

    plan = plan_doctrine_diagram_edits(
        [source],
        edge_intents=[
            {
                "kind": "mutually_exclusive",
                "source_id": "DOCTRINE_ROOT",
                "target_id": "DOCTRINE_CHILD",
                "present": True,
                "source_revision": revision,
            }
        ],
        pending_node_ids=["DOCTRINE_CHILD", "DOCTRINE_CHILD"],
    )

    assert plan["status"] == "blocked"
    assert plan["drafts"] == []
    assert {row["code"] for row in plan["diagnostics"]} >= {
        "doctrine.plan.duplicate_pending_node",
        "doctrine.plan.pending_edge_unsupported",
    }
