# API Catalog Surface Contract Alignment

## Summary

- Added a contract tying the aggregate API catalog to the static surface contract summary.
- The check derives adapter surface names from `get_surface_contract_summary()` and verifies `surface-contract-reference` is listed under each matching API catalog surface.
- The check maps the static `openapi` contract identifier to the catalog's `rest` surface name.
- Added a stale-catalog regression that removes `bundle` from the `surface-contract-reference` row and verifies the contract reports the drift.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_surfaces_match_static_surface_contracts -q` failed first because `api_catalog_surface_contract_gaps` did not exist.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_surfaces_match_static_surface_contracts tests/test_api_table_contracts.py::test_api_catalog_surfaces_flag_stale_surface_contract_reference -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk git diff --check`

## Waiver

- Full-suite tests are deferred to keep CPU free for concurrent PIHC3 migration work; this slice changes only API catalog contract tests and one progress note.
