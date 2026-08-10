# 2026-06-20 03:22 +0800 - Project facade API selector helper

## Slice

- Added `get_project_facade_api_selection(symbol=..., index_name=..., key=...)` so the `paradev.project` facade API table supports full-table, row, and module/feature/kind index projection lookups through the shared API table selector.
- Exported the helper from `paradev.project` and regenerated `docs/user-manual/project-facade-api-reference.md`, increasing the project facade API row count to 8.
- Added `tests/test_project_facade_api_selection.py` to cover table, row, index, invalid-selector, detached-row, and generated-doc parity behavior.

## Verification

- Red: `rtk uv run pytest -q tests/test_project_facade_api_selection.py` failed on missing `get_project_facade_api_selection`.
- Green: `rtk uv run pytest -q tests/test_project_facade_api_selection.py tests/test_api_table.py` -> 165 passed.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/project/api.py src/paradev/project/__init__.py tests/test_project_facade_api_selection.py` -> OK.
- Focused flake: `rtk bash scripts/flake.bash --ci --paths src/paradev/project/api.py src/paradev/project/__init__.py tests/test_project_facade_api_selection.py` -> clean after formatting the new test.

## Notes

- Regenerated the project facade reference from `render_project_facade_api_reference_markdown()` directly to avoid relying on dirty CLI files.
- Skipped the full suite to keep CPU free for concurrent PIHC2/PIHC3 migration workers.
- Staged scope should remain limited to the project facade API table module, package facade export, generated project facade reference, the focused test, and this note.
