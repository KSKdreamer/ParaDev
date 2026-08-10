# 2026-06-20 03:48 +0800 - REST facade API selector helper

## Slice
- Added `get_rest_facade_api_selection(symbol=..., index_name=..., key=...)` so the `paradev.api` REST facade table supports full-table, row, and module/feature/kind index projection lookups through the shared API table selector.
- Exported the helper from `paradev.api` and regenerated `docs/user-manual/rest-facade-api-reference.md`, increasing the REST facade API row count to 11.
- Added `tests/test_rest_facade_api_selection.py` to cover table, row, index, invalid-selector, detached-row, and generated-doc parity behavior.

## Verification
- Red: `rtk uv run pytest -q tests/test_rest_facade_api_selection.py` failed on missing `get_rest_facade_api_selection`.
- Green: `rtk uv run pytest -q tests/test_rest_facade_api_selection.py tests/test_api_table.py` -> 165 passed.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/api/api.py src/paradev/api/__init__.py tests/test_rest_facade_api_selection.py` -> OK.
- Focused flake: `rtk bash scripts/flake.bash --ci --paths src/paradev/api/api.py src/paradev/api/__init__.py tests/test_rest_facade_api_selection.py` -> clean.

## Notes
- Regenerated the REST facade reference from `render_rest_facade_api_reference_markdown()` directly to avoid relying on dirty CLI/API catalog files.
- Skipped the full suite to keep CPU free for concurrent PIHC2/PIHC3 migration workers.
- Staged scope should remain limited to the REST facade API table module, package facade export, generated REST facade reference, the focused test, and this note.
