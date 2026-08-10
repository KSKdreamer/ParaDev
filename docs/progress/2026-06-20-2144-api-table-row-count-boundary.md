# API Table Row Count Boundary

## Summary

- Tightened API table payload checks so `row_count` must be an integer, not a float or bool alias.
- Added a REST API regression for `row_count` set to `float(table["row_count"])`, which previously passed equality-only validation.
- Preserved runtime behavior and generated references; this slice only strengthens API table schema contract tests.

## Verification

- RED: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_table_payload_contract_flags_non_integer_row_count -q` failed before the helper change.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_table_payload_contract_flags_non_integer_row_count -q`.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_tables_have_auditable_reference_payloads -q`.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q` with 249 passed.
- GREEN: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`.
- GREEN: `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`.
- GREEN: `rtk git diff --check`.

## Waiver

- Skipped the full suite in this loop to reduce CPU contention while other workers continue the PIHC migration.
