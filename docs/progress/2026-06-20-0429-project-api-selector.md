# Project API Selector Progress

Date: 2026-06-20 04:29 +0800

Linear: N/A

## Done

- Added `get_project_api_selection(symbol=..., index_name=..., key=...)` to `paradev.sdk.project_api` so the Project object API table supports full-table, row, and feature/kind/CLI/frontend/inspection index projections through the shared API table selector.
- Added `tests/test_project_api_selection.py` for table, row, index, invalid-selector, and detached-row behavior.

## Verification

- Red: `rtk uv run pytest -q tests/test_project_api_selection.py` failed on missing `get_project_api_selection`.
- Green: `rtk uv run pytest -q tests/test_project_api_selection.py tests/test_api_table.py` passed with 163 tests.

## Risks Or Blockers

- Skipped generated `docs/user-manual/project-api-reference.md` parity in this slice because that file already has unrelated `module-batch-edit` changes from another active worker.
- Skipped the full suite to keep CPU available for concurrent PIHC2/PIHC3 migration work.
- Avoided dirty SDK facade, CLI surface, generated SDK/project/CLI references, and broad architecture tests.

## Next

- After the `module-batch-edit` slice lands or clears, regenerate the Project API reference and decide whether `get_project_api_selection` should also be exposed through the top-level `paradev.sdk` facade.
