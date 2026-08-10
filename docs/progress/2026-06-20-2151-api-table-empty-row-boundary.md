# API Table Empty Row Boundary

## Summary

- Tightened API table payload checks so generated API tables cannot have an empty `rows` list.
- Added a REST API regression for `rows: []`, `row_count: 0`, and empty indexes, which previously passed payload validation.
- Preserved runtime behavior and generated references; this slice only strengthens API table completeness contracts.

## Verification

- RED: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_table_payload_contract_flags_empty_rows -q` failed before the helper change.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_table_payload_contract_flags_empty_rows -q`.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_tables_have_auditable_reference_payloads -q`.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q` with 250 passed.
- GREEN: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`.
- GREEN: `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`.
- GREEN: `rtk git diff --check`.

## Waiver

- Skipped the full suite in this loop to reduce CPU contention while other workers continue the PIHC migration.
