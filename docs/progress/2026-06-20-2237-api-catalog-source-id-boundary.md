# API Catalog Source ID Boundary

## Summary

- Tightened API catalog row-shape checks so generated catalog row ids must match the canonical `API_CATALOG_SOURCE_ROWS` id set.
- Added a regression for a renamed reference id that would otherwise remain non-empty and unique while no longer matching the source catalog contract.
- Preserved runtime behavior and generated references; this slice only strengthens the aggregate API catalog contract audit layer.

## Verification

- RED: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_rows_flag_source_id_drift -q` failed before the source-id helper change.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_rows_flag_source_id_drift -q`.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_rows_have_stable_shape -q`.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q` passed with 258 tests.
- GREEN: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`.
- GREEN: `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`.
- GREEN: `rtk git diff --check`.

## Waiver

- Skipped the full suite in this loop to reduce CPU contention while other workers continue the PIHC migration.
