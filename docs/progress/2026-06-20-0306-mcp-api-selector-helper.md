# 2026-06-20 03:06 +0800 - MCP API selector helper

## Slice

- Added `get_mcp_api_selection(symbol=..., index_name=..., key=...)` to the MCP surface so callers can read the full MCP API table, one tool row, or one mode/feature/frontend-operation index projection through the shared API table selector.
- Regenerated `docs/user-manual/mcp-api-reference.md` so the MCP API reference advertises the selector helper alongside the tool table counts.
- Added `tests/test_mcp_api_selection.py` to cover table, row, index, invalid-selector, detached-list, and generated-doc parity behavior.

## Verification

- Red: `rtk uv run pytest -q tests/test_mcp_api_selection.py` failed on missing `get_mcp_api_selection`.
- Green: `rtk uv run pytest -q tests/test_mcp_api_selection.py tests/test_api_table.py` -> 164 passed.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/mcp.py tests/test_mcp_api_selection.py` -> OK.
- Focused flake: `rtk bash scripts/flake.bash --ci --paths src/paradev/surfaces/mcp.py tests/test_mcp_api_selection.py` -> clean after formatting.

## Notes

- Skipped the full suite to keep CPU free for concurrent PIHC2/PIHC3 migration workers.
- Staged scope should remain limited to the MCP surface, its generated reference, the new focused test, and this note.
