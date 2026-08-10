# API Table Typed Row Boundary

## Summary

- Tightened API table row-shape checks so emitted row fields must match the row `TypedDict` referenced by the table helper return type.
- Added regressions for missing typed row fields and stale typed row fields using the REST API table as the representative generated surface.
- Preserved runtime behavior and generated references; this slice only strengthens the API table contract audit layer.

## Verification

- RED: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_table_row_shape_flags_missing_typed_row_field tests/test_api_table_contracts.py::test_api_table_row_shape_flags_stale_typed_row_field -q` failed before the row typed-field helper change.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_table_row_shape_flags_missing_typed_row_field tests/test_api_table_contracts.py::test_api_table_row_shape_flags_stale_typed_row_field -q`.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py::test_standard_api_tables_have_stable_row_shape -q`.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q` passed with 256 tests.
- GREEN: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`.
- GREEN: `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`.
- GREEN: `rtk git diff --check`.

## Waiver

- Skipped the full suite in this loop to reduce CPU contention while other workers continue the PIHC migration.
