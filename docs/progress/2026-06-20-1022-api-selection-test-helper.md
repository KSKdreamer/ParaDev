# 2026-06-20 10:22 API selection test helper

## Summary

- Added `tests/api_selection_contracts.py` as the shared contract helper for generated API table selector tests.
- Migrated the build, copy-roots, PDX core, LSP server, and HeavenBase API selection tests to use the shared full-table, row, index, detached-copy, and invalid-selector assertions.
- Kept SDK, CLI, REST, MCP, and generated API reference behavior unchanged; this is a test-maintainability slice for API table coverage.

## Verification

- `rtk uv run pytest tests/test_build_api_selection.py tests/test_copy_roots_api_selection.py tests/test_pdx_core_api_selection.py tests/test_lsp_server_api_selection.py tests/test_hb_api_selection.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_selection_contracts.py tests/test_build_api_selection.py tests/test_copy_roots_api_selection.py tests/test_pdx_core_api_selection.py tests/test_lsp_server_api_selection.py tests/test_hb_api_selection.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_selection_contracts.py tests/test_build_api_selection.py tests/test_copy_roots_api_selection.py tests/test_pdx_core_api_selection.py tests/test_lsp_server_api_selection.py tests/test_hb_api_selection.py`
