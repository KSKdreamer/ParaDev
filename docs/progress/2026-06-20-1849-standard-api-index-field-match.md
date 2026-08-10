# Standard API Index Field Match

## Summary

- Tightened standard API table index coverage so generated lookup indexes cannot place an existing row ID under the wrong index key.
- Added a stale-contract regression that appends a `GET` REST API row to the `POST` `method_index` bucket.
- Kept runtime behavior unchanged; this slice only strengthens API table contract tests.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_standard_api_table_index_coverage_flags_wrong_index_key -q` failed first because wrong-key index membership was accepted.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_standard_api_table_index_coverage_flags_wrong_index_key tests/test_api_table_contracts.py::test_standard_api_table_index_coverage_flags_unknown_row_value tests/test_api_table_contracts.py::test_standard_api_table_index_coverage_flags_missing_row_value tests/test_api_table_contracts.py::test_standard_api_table_indexes_cover_row_fields -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk git diff --check`

## Waiver

- Full-suite tests are deferred to keep CPU free for concurrent PIHC3 migration work; this slice changes API table contract tests and one progress note only.
