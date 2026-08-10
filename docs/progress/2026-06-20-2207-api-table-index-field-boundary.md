# API Table Index Field Boundary

## Summary

- Tightened non-catalog API table payload checks so generated tables must retain at least one mapping index field.
- Added a REST API regression that strips all `_index` fields while leaving rows and row count intact.
- Preserved runtime behavior and generated references; this slice only strengthens API table grouping contracts.

## Verification

- RED: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_table_payload_contract_flags_missing_index_fields -q` failed before the helper change.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_table_payload_contract_flags_missing_index_fields -q`.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_tables_have_auditable_reference_payloads -q`.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q` passed with 252 tests.
- GREEN: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`.
- GREEN: `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`.
- GREEN: `rtk git diff --check`.

## Waiver

- Skipped the full suite in this loop to reduce CPU contention while other workers continue the PIHC migration.
