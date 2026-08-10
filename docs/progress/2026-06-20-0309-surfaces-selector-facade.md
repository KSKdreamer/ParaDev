# 2026-06-20 03:09 +0800 - Surfaces selector facade

## Slice

- Exported `get_rest_api_selection` and `get_mcp_api_selection` from `paradev.surfaces` so the aggregate surface facade exposes the selector helpers added to the REST and MCP API tables.
- Regenerated `docs/user-manual/surfaces-api-reference.md` so the surfaces facade table lists the new selector helpers and the row count now matches the current facade exports.
- Added `tests/test_surfaces_api_selection_exports.py` to cover facade exports, generated table rows, selector behavior through the facade, and generated-doc parity.

## Verification

- Red: `rtk uv run pytest -q tests/test_surfaces_api_selection_exports.py` failed on missing `get_mcp_api_selection` facade export.
- Green: `rtk uv run pytest -q tests/test_surfaces_api_selection_exports.py tests/test_rest_api_selection.py tests/test_mcp_api_selection.py` -> 9 passed.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/__init__.py src/paradev/surfaces/api.py tests/test_surfaces_api_selection_exports.py` -> OK.
- Focused flake: `rtk bash scripts/flake.bash --ci --paths src/paradev/surfaces/__init__.py src/paradev/surfaces/api.py tests/test_surfaces_api_selection_exports.py` -> clean.

## Notes

- Regenerated the surfaces reference from `render_surfaces_api_reference_markdown()` directly to avoid relying on the currently dirty CLI file.
- Skipped the full suite to keep CPU free for concurrent PIHC2/PIHC3 migration workers.
- Staged scope should remain limited to the surfaces facade, generated surfaces reference, the new focused test, and this note.
