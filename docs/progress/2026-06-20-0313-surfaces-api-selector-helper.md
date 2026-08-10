# 2026-06-20 03:13 +0800 - Surfaces API selector helper

## Slice

- Added `get_surfaces_api_selection(symbol=..., index_name=..., key=...)` to the surfaces API table module so the aggregate facade table now supports full-table, row, and index projection lookups through the shared API table selector.
- Exported the helper from `paradev.surfaces` and regenerated `docs/user-manual/surfaces-api-reference.md`, increasing the surfaces facade row count to 50.
- Extended `tests/test_surfaces_api_selection_exports.py` to cover table, row, index, invalid-selector, detached-row, export, and generated-doc parity behavior.

## Verification

- Red: `rtk uv run pytest -q tests/test_surfaces_api_selection_exports.py` failed on missing `get_surfaces_api_selection`.
- Green: `rtk uv run pytest -q tests/test_surfaces_api_selection_exports.py tests/test_rest_api_selection.py tests/test_mcp_api_selection.py tests/test_api_table.py` -> 172 passed.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/api.py src/paradev/surfaces/__init__.py tests/test_surfaces_api_selection_exports.py` -> OK.
- Focused flake: `rtk bash scripts/flake.bash --ci --paths src/paradev/surfaces/api.py src/paradev/surfaces/__init__.py tests/test_surfaces_api_selection_exports.py` -> clean.

## Notes

- Regenerated the surfaces reference from `render_surfaces_api_reference_markdown()` directly to avoid relying on the currently dirty CLI file.
- Skipped the full suite to keep CPU free for concurrent PIHC2/PIHC3 migration workers.
- Staged scope should remain limited to the surfaces API table module, facade exports, generated surfaces reference, the focused test, and this note.
