# 2026-06-20 10:01 API reference parity utility cleanup

## Summary

- Updated build, copy-roots, PDX core, LSP server, REST facade, REST, and MCP API selection tests to use `heavenbase.utils.load_txt()` for generated reference parity checks.
- Replaced the remaining facade-derived row-count literals in this group with checks against the owning public `__all__` export lists.
- Kept the slice test-only and focused on API table maintainability; no SDK, CLI, REST, or MCP behavior changed.

## Verification

- `rtk uv run pytest tests/test_build_api_selection.py tests/test_copy_roots_api_selection.py tests/test_mcp_api_selection.py tests/test_rest_api_selection.py tests/test_rest_facade_api_selection.py tests/test_pdx_core_api_selection.py tests/test_lsp_server_api_selection.py -q`
