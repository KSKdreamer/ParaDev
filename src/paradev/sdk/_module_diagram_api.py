"""Shared request validation for source-backed module diagram surfaces."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from paradev._module_diagram_contract import (
    MAX_MODULE_DIAGRAM_EDGE_INTENTS,
    MAX_MODULE_DIAGRAM_NODE_INTENTS,
    MAX_MODULE_DIAGRAM_POSITION_INTENTS,
)

_MODULE_DIAGRAM_PROVIDER_PATTERN = r"^[a-z][a-z0-9_-]*$"


def module_diagram_family_schema(
    *,
    editable: bool,
) -> dict[str, object]:
    """Return the canonical module-diagram family selector schema.

    Args:
        editable: Whether to expose only providers with a guarded source-edit
            contract.

    Returns:
        Detached open-vocabulary JSON Schema object. Active providers and
        aliases are discovered from ``project.browser`` family capabilities.
    """

    capability = "Editable" if editable else "Readable"
    return {
        "type": "string",
        "minLength": 1,
        "pattern": _MODULE_DIAGRAM_PROVIDER_PATTERN,
        "description": (
            f"{capability} registered source-backed module diagram provider "
            "id or alias. Discover active project-specific values from "
            "project.browser families[].diagram."
        ),
    }


def module_diagram_edit_input_schema(
    *,
    project_field: str,
) -> dict[str, object]:
    """Return the canonical bounded diagram-edit JSON input schema.

    Args:
        project_field: Transport-specific project-path field. REST uses
            `project_root`, while MCP uses `path`.

    Returns:
        Detached JSON Schema object for one guarded diagram edit request.

    Raises:
        ValueError: If `project_field` is not `path` or `project_root`.
    """

    if project_field not in {"path", "project_root"}:
        raise ValueError("Module diagram project field must be 'path' or 'project_root'.")
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            project_field: {
                "type": "string",
                "minLength": 1,
                "description": "Project root or nested project path.",
            },
            "family": module_diagram_family_schema(editable=True),
            "profile": {
                "anyOf": [{"type": "string", "minLength": 1}, {"type": "null"}],
                "default": None,
            },
            "position_intents": _position_intents_schema(),
            "edge_intents": _edge_intents_schema(),
            "node_intents": _node_intents_schema(),
            "write": {"type": "boolean", "default": False},
            "plan_hash": {
                "anyOf": [{"type": "string", "minLength": 1}, {"type": "null"}],
                "default": None,
            },
        },
        "required": [project_field, "family"],
        "allOf": [
            {
                "if": {
                    "properties": {"write": {"const": True}},
                    "required": ["write"],
                },
                "then": {
                    "required": ["plan_hash"],
                    "properties": {"plan_hash": {"type": "string", "minLength": 1}},
                },
            }
        ],
    }


def module_diagram_intents(
    position_intents: object = None,
    edge_intents: object = None,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Validate bounded JSON intent arrays before calling the Project SDK.

    Args:
        position_intents: Optional JSON array of absolute node-position
            intent objects.
        edge_intents: Optional JSON array of dependency/path edge intent
            objects.

    Returns:
        Detached position and edge intent mappings.

    Raises:
        ValueError: If either input is not an array of JSON objects or exceeds
            its transport limit.
    """

    return (
        _intent_rows(
            position_intents,
            name="position_intents",
            maximum=MAX_MODULE_DIAGRAM_POSITION_INTENTS,
        ),
        _intent_rows(
            edge_intents,
            name="edge_intents",
            maximum=MAX_MODULE_DIAGRAM_EDGE_INTENTS,
        ),
    )


def module_diagram_node_intents(
    node_intents: object = None,
) -> list[dict[str, object]]:
    """Validate the bounded provider-owned graph node request."""

    return _intent_rows(
        node_intents,
        name="node_intents",
        maximum=MAX_MODULE_DIAGRAM_NODE_INTENTS,
    )


def _intent_rows(
    value: object,
    *,
    name: str,
    maximum: int,
) -> list[dict[str, object]]:
    if value is None:
        return []
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        # Public JSON surfaces consistently expose malformed request shapes as
        # ValueError so CLI, REST, MCP, and desktop adapters can normalize them.
        raise ValueError(f"Module diagram {name} must be a JSON array.")  # noqa: TRY004
    if len(value) > maximum:
        raise ValueError(f"Module diagram {name} cannot contain more than {maximum} intents.")
    rows: list[dict[str, object]] = []
    for index, row in enumerate(value):
        if not isinstance(row, Mapping):
            raise ValueError(f"Module diagram {name}[{index}] must be a JSON object.")  # noqa: TRY004
        if any(not isinstance(key, str) for key in row):
            raise ValueError(f"Module diagram {name}[{index}] field names must be strings.")
        rows.append(dict(row))
    return rows


def _position_intents_schema() -> dict[str, object]:
    return {
        "type": "array",
        "maxItems": MAX_MODULE_DIAGRAM_POSITION_INTENTS,
        "default": [],
        "items": {
            "type": "object",
            "description": ("Provider-specific position intent. The selected registered " "provider performs authoritative runtime validation."),
        },
    }


def _edge_intents_schema() -> dict[str, object]:
    return {
        "type": "array",
        "maxItems": MAX_MODULE_DIAGRAM_EDGE_INTENTS,
        "default": [],
        "items": {
            "type": "object",
            "description": ("Provider-specific relationship intent. The selected " "registered provider performs authoritative runtime validation."),
        },
    }


def _node_intents_schema() -> dict[str, object]:
    return {
        "type": "array",
        "maxItems": MAX_MODULE_DIAGRAM_NODE_INTENTS,
        "default": [],
        "items": {
            "type": "object",
            "description": (
                "One provider-specific node creation intent. Discover its "
                "visible fields and selected-node defaults from "
                "project.browser families[].diagram.node_authoring."
            ),
        },
    }
