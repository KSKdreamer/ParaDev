# API Catalog Source Metadata Boundary

## Summary

- Tightened API catalog row-shape checks so generated catalog source fields must match the canonical `API_CATALOG_SOURCE_ROWS` entries for the same id.
- Added a regression for masked source metadata drift where `sdk-api` keeps its id but changes its title and declared surfaces.
- Preserved runtime behavior and generated references; this slice only strengthens the aggregate API catalog contract audit layer.

## Verification

- RED: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_rows_flag_source_metadata_drift -q` failed before the source metadata helper change.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_rows_flag_source_metadata_drift -q`.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_rows_have_stable_shape -q`.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q` passed with 259 tests.
- GREEN: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`.
- GREEN: `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`.
- GREEN: `rtk git diff --check`.

## Waiver

- Skipped the full suite in this loop to reduce CPU contention while other workers continue the PIHC migration.
