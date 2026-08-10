# 2026-06-20 03:17 +0800 - Localization API selector helper

## Slice

- Added `get_localization_api_selection(symbol=..., index_name=..., key=...)` so the localization facade API table supports full-table, row, and module/feature/kind index projection lookups through the shared API table selector.
- Exported the helper from `paradev.localization` and regenerated `docs/user-manual/localization-api-reference.md`, increasing the localization facade row count to 8.
- Added `tests/test_localization_api_selection.py` to cover table, row, index, invalid-selector, detached-row, and generated-doc parity behavior.

## Verification

- Red: `rtk uv run pytest -q tests/test_localization_api_selection.py` failed on missing `get_localization_api_selection`.
- Green: `rtk uv run pytest -q tests/test_localization_api_selection.py tests/test_api_table.py` -> 165 passed.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/localization/api.py src/paradev/localization/__init__.py tests/test_localization_api_selection.py` -> OK.
- Focused flake: `rtk bash scripts/flake.bash --ci --paths src/paradev/localization/api.py src/paradev/localization/__init__.py tests/test_localization_api_selection.py` -> clean after formatting.

## Notes

- Regenerated the localization reference from `render_localization_api_reference_markdown()` directly to avoid relying on dirty CLI files.
- Skipped the full suite to keep CPU free for concurrent PIHC2/PIHC3 migration workers.
- Staged scope should remain limited to the localization API table module, package facade export, generated localization reference, the focused test, and this note.
