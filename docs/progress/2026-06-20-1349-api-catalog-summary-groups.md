# API Catalog Summary Groups

## Summary

- Added a shared contract that verifies API catalog summary counts match the generated table indexes and reference group payloads.
- Added reference-group partition checks so every catalog reference id is assigned to exactly one reader-facing group.
- Refactored the test helper to share API catalog table/row validation across catalog contracts.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_summary_and_reference_groups_are_consistent -q` failed first because `api_catalog_summary_group_gaps` did not exist.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_summary_and_reference_groups_are_consistent -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`

## Waiver

- Full-suite tests were skipped to reduce CPU use while other workers are active; this slice only changes shared API contract tests.
