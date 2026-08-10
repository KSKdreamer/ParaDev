# 2026-06-15 12:16 surface index header helper

## Scope

- Generalized `api_index_table_header(...)` with optional count/value column labels.
- Reused the shared index header helper in the CLI, REST, and MCP API reference renderers.
- Removed one-line local index-row wrapper functions from the CLI, REST, and MCP surface tables.
- Kept rendered Markdown text, API table payloads, schema anchors, and indexes unchanged.
- Left unrelated desktop, skill, PIHC3, localization, and logo worktree edits untouched.

## Verification

- Renderer/table comparison against `HEAD` passed for 19 API reference modules, including CLI, REST, and MCP.
- `rtk bash scripts/test.bash tests/test_api_table.py ... -q` with CLI, REST, MCP, and surface architecture anchors.
- `rtk uv run python -m py_compile ...` for the shared helper, touched surface modules, and `tests/test_api_table.py`.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py ...`
- `rtk bash scripts/flake.bash --ci --paths ...`
- Full test suite deferred to reduce CPU while other migration workers are active.

## Git hygiene

- Stage only the shared markdown helper, touched surface API modules, `tests/test_api_table.py`, and this note.
- Do not stage `node_modules/`.
