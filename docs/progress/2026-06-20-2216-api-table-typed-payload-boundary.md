# API Table Typed Payload Boundary

## Summary

- Tightened API table payload checks so each generated table must match the `TypedDict` returned by its table helper.
- Added regressions for missing typed index fields and stale typed index fields while keeping the runtime table payload otherwise valid.
- Preserved runtime behavior and generated references; this slice only strengthens the API table contract audit layer.

## Verification

- RED: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_table_payload_contract_flags_missing_typed_index_field -q` failed before the typed-field helper change.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_table_payload_contract_flags_missing_typed_index_field -q`.
- RED: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_table_payload_contract_flags_stale_typed_index_field -q` failed before stale typed-field detection.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_table_payload_contract_flags_missing_typed_index_field tests/test_api_table_contracts.py::test_api_table_payload_contract_flags_stale_typed_index_field -q`.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_tables_have_auditable_reference_payloads -q`.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q` passed with 254 tests.
- GREEN: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`.
- GREEN: `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`.
- GREEN: `rtk git diff --check`.

## Waiver

- Skipped the full suite in this loop to reduce CPU contention while other workers continue the PIHC migration.
