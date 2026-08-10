# API Catalog Index Coverage

## Summary

- Added a shared contract that verifies API catalog rows are present in the indexes implied by their row fields.
- Covered scalar indexes such as layer, feature, kind, owner module, CLI command, selector helper, and doc page, plus multi-value surface indexes.
- Preserved selector-helper optionality for rows that do not expose a selector helper.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_indexes_cover_row_fields -q` failed first because `api_catalog_index_coverage_gaps` did not exist.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_indexes_cover_row_fields -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`

## Waiver

- Full-suite tests were skipped to reduce CPU use while other workers are active; this slice only changes shared API contract tests.
