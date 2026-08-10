# API Catalog Self Metadata Boundary

## Summary

- Tightened the API catalog metadata audit so the `api-catalog` row compares against the canonical catalog source module, not a potentially patched package-level catalog table.
- Added a regression for self-referential index metadata drift where both the catalog row and returned table lose `surface_index`.
- Preserved runtime behavior and generated references; this slice only strengthens the aggregate API catalog contract audit layer.

## Verification

- RED: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_metadata_contract_flags_self_reference_index_drift -q` failed before the helper change.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_metadata_contract_flags_self_reference_index_drift -q`.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_rows_match_source_helper_metadata -q`.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q` passed with 257 tests.
- GREEN: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`.
- GREEN: `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`.
- GREEN: `rtk git diff --check`.

## Waiver

- Skipped the full suite in this loop to reduce CPU contention while other workers continue the PIHC migration.
