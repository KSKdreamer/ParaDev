# 2026-06-20 10:10 REST and MCP selector count alignment

## Summary

- Updated `tests/test_cli_api_rest_mcp_selectors.py` so REST and MCP API row-count assertions read from `get_rest_api_table()` and `get_mcp_api_table()` instead of copied literals.
- Kept the slice focused on selector/API catalog contract tests and avoided broad architecture or CLI test files that have unrelated main-checkout work in progress.
- Preserved API behavior; this is a test-contract maintainability cleanup.

## Verification

- `rtk uv run pytest tests/test_cli_api_rest_mcp_selectors.py -q`
