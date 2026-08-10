# API Catalog Test Anchor Boundary

## Summary

- Tightened API catalog reference checks so each aggregate catalog row `test_anchor` must point at an existing `tests/*.py` function.
- Added a regression that changes the `api-catalog` row to point at `src/paradev/cli.py::main`, proving catalog rows now reject non-test anchors like standard API tables do.
- Preserved runtime behavior and generated references; this slice only strengthens the API catalog reference audit layer.

## Verification

- RED: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_reference_contract_flags_non_tests_anchor -q` failed before the catalog test-anchor helper.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_reference_contract_flags_non_tests_anchor -q`.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_references_match_generated_manual_pages -q`.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q` passed with 262 tests.
- GREEN: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`.
- GREEN: `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`.
- GREEN: `rtk git diff --check`.

## Waiver

- Skipped the full suite in this loop to reduce CPU contention while other workers continue the PIHC migration.
