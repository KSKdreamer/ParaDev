# API Catalog Index Field Match

## Summary

- Tightened API catalog index coverage so generated lookup indexes cannot place an existing reference ID under the wrong index key.
- Added a stale-contract regression that appends `sdk-api` to the `surface` `layer_index` bucket even though its catalog row belongs to the `sdk` layer.
- Kept runtime behavior unchanged; this slice only strengthens API catalog contract tests.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_indexes_flag_wrong_index_key -q` failed first because wrong-key catalog index membership was accepted.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_indexes_flag_wrong_index_key tests/test_api_table_contracts.py::test_api_catalog_indexes_flag_unknown_reference_ids tests/test_api_table_contracts.py::test_api_catalog_indexes_cover_row_fields -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk git diff --check`

## Waiver

- Full-suite tests are deferred to keep CPU free for concurrent PIHC3 migration work; this slice changes API catalog contract tests and one progress note only.
