# API Table Selector Contract Progress

Date: 2026-06-20 04:38 +0800

Linear: N/A

## Done

- Added `tests/test_api_table_contracts.py` to enforce that every `src/paradev` module defining a `get_*api_table` helper also exposes a selector helper or uses the shared `api_table_selection` utility.
- Used AST function definitions for the scan so modules that merely mention API tables do not create false positives.

## Verification

- Red: `rtk uv run pytest -q tests/test_api_table_contracts.py tests/test_api_table.py` initially failed on `src/paradev/sdk/project.py`, which mentioned API tables without defining one.
- Green: `rtk uv run pytest -q tests/test_api_table_contracts.py tests/test_api_table.py` passed with 162 tests after tightening the contract check.

## Risks Or Blockers

- This slice is a regression guard only; generated SDK/project/CLI references remain deferred because they are currently dirty from another active `module-batch-edit` slice.
- Skipped the full suite to keep CPU available for concurrent PIHC2/PIHC3 migration work.

## Next

- Once the generated reference files are no longer owned by another slice, sync `get_sdk_api_selection`, `get_project_api_selection`, and `get_cli_api_selection` into the relevant facade/docs tables where appropriate.
