# API Table Index Coverage Contract

## Summary

- Added a generic contract that checks generated API table indexes are complete from row fields back to row keys.
- The existing payload check already rejected dangling index values; this closes the opposite gap where a row can be missing from an index.
- The helper infers common index fields such as `method_index -> method`, `frontend_operation_index -> frontend_operation_ids`, and `cli_command_index -> cli_commands`.
- Empty optional indexed fields are treated as intentionally unindexed values.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_standard_api_table_indexes_cover_row_fields -q` failed first because `api_table_index_coverage_gaps` did not exist.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_standard_api_table_indexes_cover_row_fields tests/test_api_table_contracts.py::test_standard_api_table_index_coverage_flags_missing_row_value -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk git diff --check`

## Waiver

- Full-suite tests are deferred to keep CPU free for concurrent PIHC3 migration work; this slice changes only API table contract tests and one progress note.
