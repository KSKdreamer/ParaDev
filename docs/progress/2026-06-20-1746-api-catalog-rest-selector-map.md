# API Catalog REST Selector Map

## Summary

- Tightened API catalog REST parity checks so selector-style REST routes must be represented in the catalog feature-to-reference map.
- The shared helper now treats `/api-catalog`, `/surface-contracts`, and `*-api` REST paths as API selector routes that require an API catalog reference mapping.
- Added a stale-contract regression that injects a `/new-api` REST selector route without a catalog mapping.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_selector_surfaces_flag_unmapped_rest_selector_route -q` failed first because unmapped REST selector routes were ignored.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_selector_surfaces_flag_unmapped_rest_selector_route tests/test_api_table_contracts.py::test_api_catalog_selector_surfaces_match_rest_and_mcp_tables -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk git diff --check`

## Waiver

- Full-suite tests are deferred to keep CPU free for concurrent PIHC3 migration work; this slice changes only API catalog contract tests and one progress note.
