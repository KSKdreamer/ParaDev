"""Dependency-free schema fragments shared by static and live REST contracts."""

from __future__ import annotations

NONBLANK_RUN_ID_PATTERN = r".*\S.*"


def nonblank_run_id_schema() -> dict[str, object]:
    """Return the JSON Schema fragment for one exact build run id."""

    return {"type": "string", "minLength": 1, "pattern": NONBLANK_RUN_ID_PATTERN}


def desktop_build_interrupt_request_schema() -> dict[str, object]:
    """Return the alias-aware exact-run interrupt request schema."""

    return {
        "type": "object",
        "additionalProperties": False,
        "anyOf": [
            {
                "required": ["runId"],
                "properties": {"runId": nonblank_run_id_schema()},
            },
            {
                "required": ["run_id"],
                "properties": {"run_id": nonblank_run_id_schema()},
            },
        ],
        "properties": {
            "runId": {"anyOf": [nonblank_run_id_schema(), {"type": "null"}]},
            "run_id": {"anyOf": [nonblank_run_id_schema(), {"type": "null"}]},
        },
    }
