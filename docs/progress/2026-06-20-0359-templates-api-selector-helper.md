# 2026-06-20 03:59 +0800 - Templates API selector helper

## Slice
- Added `get_templates_api_selection(symbol=..., index_name=..., key=...)` so the `paradev.sdk.templates` API table supports full-table, row, and module/feature/kind index projection lookups through the shared API table selector.
- Updated the `paradev.sdk.templates` public module table and regenerated `docs/user-manual/templates-api-reference.md`, increasing the templates API row count to 16.
- Added `tests/test_templates_api_selection.py` to cover table, row, index, invalid-selector, detached-row, and generated-doc parity behavior.

## Verification
- Red: `rtk uv run pytest -q tests/test_templates_api_selection.py` failed on missing `get_templates_api_selection`.
- Green: `rtk uv run pytest -q tests/test_templates_api_selection.py tests/test_api_table.py` -> 165 passed.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/templates.py tests/test_templates_api_selection.py` -> OK.
- Focused flake: `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/templates.py tests/test_templates_api_selection.py` -> clean.

## Notes
- Regenerated the templates reference from `render_templates_api_reference_markdown()` directly to avoid relying on dirty CLI/API catalog files.
- Avoided `src/paradev/sdk/__init__.py`, which is already dirty from concurrent API/migration work.
- Skipped the full suite to keep CPU free for concurrent PIHC2/PIHC3 migration workers.
- Staged scope should remain limited to the templates API table module, generated templates reference, the focused test, and this note.
