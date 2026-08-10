# API Catalog Metadata Contract

## Summary

- Added a shared contract that verifies API catalog rows match their source `table_helper` metadata for `schema`, `row_count`, and `index_names`.
- Kept the check independent in the test helper so stale catalog metadata fails in the focused API contract suite.
- Avoided production catalog edits because `src/paradev/surfaces/api_catalog.py` is dirty in the main checkout from parallel work.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_rows_match_source_helper_metadata -q` failed first because `api_catalog_payload_metadata_gaps` did not exist.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_rows_match_source_helper_metadata -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`

## Waiver

- Full-suite tests were skipped to reduce CPU use while other workers are active; this slice only changes shared API contract tests.
