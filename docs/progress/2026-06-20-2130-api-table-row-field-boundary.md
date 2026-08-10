# API Table Row Field Boundary

## Summary

- Tightened API table row-shape checks so non-catalog API tables must keep one stable payload field set across rows.
- Added a REST API regression for a row that drops `inputs` and adds an undocumented `stale_field`.
- Kept runtime behavior and generated API references unchanged; this slice only strengthens the contract tests around fixed API table payloads.

## Verification

- RED: `rtk uv run pytest tests/test_api_table_contracts.py::test_standard_api_tables_flag_row_field_set_drift -q` failed before the helper change.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py::test_standard_api_tables_flag_row_field_set_drift tests/test_api_table_contracts.py::test_standard_api_tables_have_stable_row_shape -q`.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q` with 247 passed.
- GREEN: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`.
- GREEN: `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`.
- GREEN: `rtk git diff --check`.

## Waiver

- Skipped the full suite in this loop to reduce CPU contention while other workers continue the PIHC migration.
