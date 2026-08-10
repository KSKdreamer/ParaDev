# API Catalog Selector Surface Contract

## Summary

- Added a contract that ties REST and MCP selector exposure back to the aggregate API catalog.
- The check verifies existing REST selector route features and MCP selector tools are represented by catalog rows that advertise the matching `rest` or `mcp` surface.
- The check treats selector helpers as one-to-many because `get_frontend_api_selection` is intentionally shared by multiple catalog rows.
- Added a stale-metadata regression that removes `mcp` from the `frontend-api` catalog row and verifies the contract reports the drift.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_selector_surfaces_match_rest_and_mcp_tables -q` failed first because `api_catalog_selector_surface_gaps` did not exist.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_selector_surfaces_match_rest_and_mcp_tables tests/test_api_table_contracts.py::test_api_catalog_selector_surfaces_flag_stale_mcp_metadata -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk git diff --check`

## Waiver

- Full-suite tests are deferred to keep CPU free for concurrent PIHC3 migration work; this slice changes only API catalog contract tests and one progress note.
