# API Table Row Shape Contract

## Summary

- Added a generic row-shape contract for API-standard tables.
- The check skips the aggregate API catalog because it has its own catalog-specific schema contract.
- The check requires non-catalog API table rows to keep shared reference fields populated: `kind`, `layer`, `returns`, `surface`, and `registry_seam`.
- The check also requires `feature` whenever a table declares `feature_index`.
- Added a stale-row regression that blanks one row's `surface` value and verifies the contract reports the drift.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_standard_api_tables_have_stable_row_shape -q` failed first because `api_table_row_shape_gaps` did not exist.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_standard_api_tables_have_stable_row_shape tests/test_api_table_contracts.py::test_standard_api_tables_flag_empty_shared_row_field -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk git diff --check`

## Waiver

- Full-suite tests are deferred to keep CPU free for concurrent PIHC3 migration work; this slice changes only API table contract tests and one progress note.
