# API Catalog Payload Surface Boundary

## Summary

- Tightened API catalog payload metadata checks so catalog row `surfaces` must cover every concrete surface exposed by the referenced API table payload `surface_index`.
- Added a regression that patches `paradev.sdk.get_architecture_api_table()` with a new `desktop` surface while leaving the static catalog source row unchanged.
- Preserved runtime behavior and generated references; this slice only strengthens the aggregate API catalog contract audit layer.

## Verification

- RED: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_metadata_contract_flags_missing_payload_surface -q` failed before the payload-surface helper hook.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_metadata_contract_flags_missing_payload_surface -q`.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_rows_match_source_helper_metadata -q`.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q` passed with 261 tests.
- GREEN: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`.
- GREEN: `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`.
- GREEN: `rtk git diff --check`.

## Waiver

- Skipped the full suite in this loop to reduce CPU contention while other workers continue the PIHC migration.
