# API Catalog Index Reference IDs

## Summary

- Tightened API catalog index coverage so generated lookup indexes cannot point at unknown catalog reference IDs.
- Added a stale-contract regression that appends `stale-reference` to a `doc_page_index` bucket.
- Kept runtime API behavior unchanged; this slice only strengthens API catalog contract tests.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_indexes_flag_unknown_reference_ids -q` failed first because stale index reference IDs were ignored.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_indexes_flag_unknown_reference_ids tests/test_api_table_contracts.py::test_api_catalog_indexes_cover_row_fields -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk git diff --check`

## Waiver

- Full-suite tests are deferred to keep CPU free for concurrent PIHC3 migration work; this slice changes API catalog contract tests and one progress note only.
