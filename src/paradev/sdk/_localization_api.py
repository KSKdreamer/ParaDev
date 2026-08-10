"""Shared input schemas for Registry-owned localization authoring."""

from __future__ import annotations

from paradev.localization._authoring import (
    MAX_LOCALIZATION_WORKSPACE_LIMIT,
    MAX_LOCALIZATION_WORKSPACE_ROWS,
)


def localization_drafts_input_schema() -> dict[str, object]:
    """Return the shared unsaved-localization-draft input schema.

    Returns:
        Fresh JSON Schema for bounded source-path and text draft rows.
    """

    return {
        "type": "array",
        "items": {
            "type": "object",
            "additionalProperties": False,
            "required": ["source_path", "text"],
            "properties": {
                "source_path": {"type": "string", "minLength": 1},
                "text": {"type": "string"},
            },
        },
    }


def localization_operation_input_schema() -> dict[str, object]:
    """Return the closed localization-operation input schema.

    Returns:
        Fresh discriminated JSON Schema for ``set``, ``add``, ``rename``,
        and ``remove`` operations.
    """

    source_path = {"type": "string", "minLength": 1}
    key = {"type": "string", "minLength": 1}
    return {
        "oneOf": [
            {
                "type": "object",
                "additionalProperties": False,
                "required": ["op", "language", "key", "value"],
                "properties": {
                    "op": {"const": "set"},
                    "language": {"type": "string", "minLength": 1},
                    "key": dict(key),
                    "value": {"type": "string"},
                    "source_path": dict(source_path),
                },
            },
            {
                "type": "object",
                "additionalProperties": False,
                "required": ["op"],
                "properties": {
                    "op": {"const": "add"},
                    "key": dict(key),
                    "languages": {
                        "type": "array",
                        "minItems": 1,
                        "uniqueItems": True,
                        "items": {"type": "string", "minLength": 1},
                    },
                    "source_path": dict(source_path),
                },
            },
            {
                "type": "object",
                "additionalProperties": False,
                "required": ["op", "key", "new_key"],
                "properties": {
                    "op": {"const": "rename"},
                    "key": dict(key),
                    "new_key": dict(key),
                },
            },
            {
                "type": "object",
                "additionalProperties": False,
                "required": ["op", "key"],
                "properties": {
                    "op": {"const": "remove"},
                    "key": dict(key),
                },
            },
        ]
    }


def localization_request_input_properties(*, include_operation: bool) -> dict[str, object]:
    """Return shared source-unit localization request properties.

    Args:
        include_operation: Include the required planner operation property.

    Returns:
        Fresh JSON Schema property mapping shared by REST and MCP adapters.
    """

    properties: dict[str, object] = {
        "target_kind": {
            "type": "string",
            "enum": ["module", "collection"],
            "description": "Kind of Registry-owned authoring source unit.",
        },
        "target_id": {
            "type": "string",
            "minLength": 1,
            "description": ("Canonical family/object_id module identity or collection id."),
        },
        "family": {
            "type": ["string", "null"],
            "description": "Optional collection-family disambiguator.",
        },
        "source_root": {"type": ["string", "null"]},
        "drafts": localization_drafts_input_schema(),
        "limit": {
            "type": "integer",
            "minimum": 1,
            "maximum": MAX_LOCALIZATION_WORKSPACE_LIMIT,
            "default": MAX_LOCALIZATION_WORKSPACE_ROWS,
        },
    }
    if include_operation:
        properties["operation"] = localization_operation_input_schema()
    return properties


def localization_request_required_fields(*, include_operation: bool) -> list[str]:
    """Return required fields for one localization request.

    Args:
        include_operation: Require the closed planner operation field.

    Returns:
        Ordered required field names excluding the surface-owned project path.
    """

    return [
        "target_kind",
        "target_id",
        *(("operation",) if include_operation else ()),
    ]
