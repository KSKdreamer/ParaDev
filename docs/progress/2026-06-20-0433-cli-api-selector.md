# CLI API Selector Progress

Date: 2026-06-20 04:33 +0800

Linear: N/A

## Done

- Added `get_cli_api_selection(symbol=..., index_name=..., key=...)` to `paradev.surfaces.cli` so the CLI API table supports full-table, row, and feature/kind/adapter/frontend index projections through the shared API table selector.
- Added `tests/test_cli_api_selection.py` for table, row, index, invalid-selector, and detached-row behavior.

## Verification

- Red: `rtk uv run pytest -q tests/test_cli_api_selection.py` failed on missing `get_cli_api_selection`.
- Green: `rtk uv run pytest -q tests/test_cli_api_selection.py tests/test_api_table.py` passed with 163 tests.

## Risks Or Blockers

- `src/paradev/surfaces/cli.py` and `docs/user-manual/cli-api-reference.md` already had unrelated `module-batch-edit` changes, so this slice stages only the selector helper hunks plus its focused test and note.
- Skipped generated CLI reference parity to avoid committing another worker's CLI contract changes.
- Skipped the full suite to keep CPU available for concurrent PIHC2/PIHC3 migration work.

## Next

- After the `module-batch-edit` slice lands or clears, regenerate the CLI API reference and decide whether `paradev cli-api` should expose row/index selectors like `api-catalog` and `frontend-api`.
