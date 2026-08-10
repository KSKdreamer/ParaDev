# API Catalog Surface Vocabulary

## Summary

- Tightened API catalog row-shape checks so `surfaces` entries must use known public surface tokens.
- Added a stale-contract regression that injects `stale-surface` into a catalog row and expects a row-shape gap.
- Kept the slice test-only so runtime behavior and generated API catalog output remain unchanged.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_rows_flag_unknown_surface -q` failed first because unknown surface tokens were accepted.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_rows_flag_unknown_surface tests/test_api_table_contracts.py::test_api_catalog_rows_have_stable_shape -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk git diff --check`

## Waiver

- Full-suite tests are deferred to keep CPU free for concurrent PIHC3 migration work; this slice changes API catalog contract tests and one progress note only.
