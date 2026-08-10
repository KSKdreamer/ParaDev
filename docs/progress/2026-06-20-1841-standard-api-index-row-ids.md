# Standard API Index Row IDs

## Summary

- Tightened standard API table index coverage so generated lookup indexes cannot point at unknown row IDs.
- Reused the existing index-value validator from payload checks inside `api_table_index_coverage_gaps()`.
- Added a stale-contract regression that appends `stale-rest-api-row` to the REST API `method_index`.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_standard_api_table_index_coverage_flags_unknown_row_value -q` failed first because stale index row IDs were ignored.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_standard_api_table_index_coverage_flags_unknown_row_value tests/test_api_table_contracts.py::test_standard_api_table_index_coverage_flags_missing_row_value tests/test_api_table_contracts.py::test_standard_api_table_indexes_cover_row_fields -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk git diff --check`

## Waiver

- Full-suite tests are deferred to keep CPU free for concurrent PIHC3 migration work; this slice changes API table contract tests and one progress note only.
