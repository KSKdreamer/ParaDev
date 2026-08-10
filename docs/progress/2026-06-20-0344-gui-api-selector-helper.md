# 2026-06-20 03:44 +0800 - GUI API selector helper

## Slice
- Added `get_gui_api_selection(symbol=..., index_name=..., key=...)` so the `paradev.gui` facade API table supports full-table, row, and module/feature/kind index projection lookups through the shared API table selector.
- Exported the helper from `paradev.gui` and regenerated `docs/user-manual/gui-api-reference.md`, increasing the GUI API row count to 8.
- Added `tests/test_gui_api_selection.py` to cover table, row, index, invalid-selector, detached-row, and generated-doc parity behavior.

## Verification
- Red: `rtk uv run pytest -q tests/test_gui_api_selection.py` failed on missing `get_gui_api_selection`.
- Green: `rtk uv run pytest -q tests/test_gui_api_selection.py tests/test_api_table.py` -> 165 passed.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/gui_api.py src/paradev/gui.py tests/test_gui_api_selection.py` -> OK.
- Focused flake: `rtk bash scripts/flake.bash --ci --paths src/paradev/gui_api.py src/paradev/gui.py tests/test_gui_api_selection.py` -> clean.

## Notes
- Regenerated the GUI reference from `render_gui_api_reference_markdown()` directly to avoid relying on dirty CLI files.
- Skipped the full suite to keep CPU free for concurrent PIHC2/PIHC3 migration workers.
- Staged scope should remain limited to the GUI API table module, GUI facade export, generated GUI reference, the focused test, and this note.
