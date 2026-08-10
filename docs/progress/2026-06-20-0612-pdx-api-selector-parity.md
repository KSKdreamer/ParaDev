# 2026-06-20 06:12 - PDX API selector parity

## Focus

Kept the API-table maintenance surface consistent by exposing the existing PDX API selector over REST and MCP, matching the architecture/catalog selector pattern.

## Changes

- Added `GET /pdx-api` as the REST selector for `get_pdx_api_selection(...)`.
- Added the read-only `pdx_api` MCP selector tool.
- Updated the PDX, REST, MCP, API catalog, and architecture references for the new public rows.
- Added focused selector tests and updated existing exact-count API-table assertions.

## Verification

- `rtk uv run --extra dev pytest -q tests/test_pdx_api_surface_selectors.py tests/test_pdx_api_selection.py tests/test_rest_api_selection.py tests/test_mcp_api_selection.py tests/test_mcp_architecture_api_selectors.py tests/test_rest_architecture_api_selectors.py`
- Broader staged verification to run from a clean staged worktree because the main checkout contains unrelated SDK/project/desktop/PIHC changes.
