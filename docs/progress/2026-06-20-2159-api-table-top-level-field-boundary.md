# API Table Top-Level Field Boundary

## Summary

- Tightened non-catalog API table payload checks so top-level fields are limited to `schema`, `row_count`, `rows`, and mapping index fields.
- Added a REST API regression for an undocumented `stale_metadata` top-level field.
- Preserved runtime behavior and generated references; this slice only strengthens API table payload schema contracts.

## Verification

- RED: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_table_payload_contract_flags_undocumented_table_field -q` failed before the helper change.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_table_payload_contract_flags_undocumented_table_field -q`.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_tables_have_auditable_reference_payloads -q`.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q` with 251 passed.
- GREEN: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`.
- GREEN: `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`.
- GREEN: `rtk git diff --check`.

## Waiver

- Skipped the full suite in this loop to reduce CPU contention while other workers continue the PIHC migration.
