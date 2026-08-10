# 2026-06-20 03:26 +0800 - Package API selector helper

## Slice

- Added `get_package_api_selection(symbol=..., index_name=..., key=...)` so the root `paradev` package API table supports full-table, row, and module/feature/kind index projection lookups through the shared API table selector.
- Exported the helper from `paradev` and regenerated `docs/user-manual/package-api-reference.md`, increasing the package API row count to 15.
- Added `tests/test_package_api_selection.py` to cover table, row, index, invalid-selector, detached-row, and generated-doc parity behavior.

## Verification

- Red: `rtk uv run pytest -q tests/test_package_api_selection.py` failed on missing `get_package_api_selection`.
- Green: `rtk uv run pytest -q tests/test_package_api_selection.py tests/test_api_table.py` -> 165 passed.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/package_api.py src/paradev/__init__.py tests/test_package_api_selection.py` -> OK.
- Focused flake: `rtk bash scripts/flake.bash --ci --paths src/paradev/package_api.py src/paradev/__init__.py tests/test_package_api_selection.py` -> clean.

## Notes

- Regenerated the package reference from `render_package_api_reference_markdown()` directly to avoid relying on dirty CLI files.
- Skipped the full suite to keep CPU free for concurrent PIHC2/PIHC3 migration workers.
- Staged scope should remain limited to the package API table module, root package facade export, generated package reference, the focused test, and this note.
