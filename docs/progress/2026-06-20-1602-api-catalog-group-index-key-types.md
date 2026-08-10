# API Catalog Group Index Key Types Contract

## Summary

- Added API catalog reference-group validation for `group_index` key types.
- The summary/group contract now reports non-string group ids before checking parity against `reference_groups`.
- This keeps the public selector index bounded to stable string ids, matching the reader-facing reference-group rows and `get_api_catalog_reference_group(group)` API.
- Added a regression that injects integer key `42` into `group_index` and verifies the invalid key is reported.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_reference_groups_flag_non_string_group_index_key -q` failed first because non-string `group_index` keys were ignored.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_summary_and_reference_groups_are_consistent tests/test_api_table_contracts.py::test_api_catalog_reference_groups_flag_non_string_group_index_key -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk git diff --check`

## Waiver

- Full-suite tests are deferred to keep CPU free for concurrent PIHC3 migration work; this slice changes only API table contract tests and one progress note.
