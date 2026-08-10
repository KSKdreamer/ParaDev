# API Catalog Group Index Parity Contract

## Summary

- Added API catalog reference-group parity checks between `group_index` and `reference_groups`.
- The summary/group contract now reports any `group_index` key without reader-facing group metadata, and any reference-group metadata row missing from the selector index.
- This protects the aggregate API catalog from exposing a selectable group id that lacks a title, usage text, and stable reference-group row.
- Added a stale-index regression that injects `stale-group` into `group_index` and verifies the drift is reported.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_reference_groups_flag_stale_group_index_key -q` failed first because extra `group_index` keys were not checked.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_summary_and_reference_groups_are_consistent tests/test_api_table_contracts.py::test_api_catalog_reference_groups_flag_stale_group_index_key -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk git diff --check`

## Waiver

- Full-suite tests are deferred to keep CPU free for concurrent PIHC3 migration work; this slice changes only API table contract tests and one progress note.
