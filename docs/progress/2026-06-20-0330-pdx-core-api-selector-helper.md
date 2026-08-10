# 2026-06-20 03:30 +0800 - PDX core API selector helper

## Slice

- Added `get_pdx_core_api_selection(symbol=..., index_name=..., key=...)` so the `paradev.pdx` facade API table supports full-table, row, and module/feature/kind index projection lookups through the shared API table selector.
- Exported the helper from `paradev.pdx` and regenerated `docs/user-manual/pdx-core-api-reference.md`, increasing the PDX core API row count to 23.
- Added `tests/test_pdx_core_api_selection.py` to cover table, row, index, invalid-selector, detached-row, and generated-doc parity behavior.

## Verification

- Red: `rtk uv run pytest -q tests/test_pdx_core_api_selection.py` failed on missing `get_pdx_core_api_selection`.
- Green: `rtk uv run pytest -q tests/test_pdx_core_api_selection.py tests/test_api_table.py` -> 165 passed.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/pdx/api.py src/paradev/pdx/__init__.py tests/test_pdx_core_api_selection.py` -> OK.
- Focused flake: `rtk bash scripts/flake.bash --ci --paths src/paradev/pdx/api.py src/paradev/pdx/__init__.py tests/test_pdx_core_api_selection.py` -> clean.

## Notes

- Regenerated the PDX core reference from `render_pdx_core_api_reference_markdown()` directly to avoid relying on dirty CLI files.
- Skipped the full suite to keep CPU free for concurrent PIHC2/PIHC3 migration workers.
- Staged scope should remain limited to the PDX core API table module, package facade export, generated PDX core reference, the focused test, and this note.
