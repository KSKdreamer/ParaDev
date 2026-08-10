# 2026-06-20 LSP API selector surface

Aligned the LSP API table with the existing PDX API selector pattern.

- Added REST `GET /lsp-api` and MCP `lsp_api` wrappers over `get_lsp_api_selection(...)`.
- Updated the aggregate API catalog so `lsp-api` advertises SDK, CLI, REST, MCP, LSP, and docs coverage.
- Regenerated the LSP, REST, MCP, and API catalog reference rows that changed.
- Added focused tests for REST/MCP LSP selector parity without running the full suite.

Targeted verification:

```bash
rtk uv run --extra dev --extra rest pytest -q tests/test_lsp_api_surface_selectors.py tests/test_lsp_api_selection.py
```

The dirty main worktree currently has unrelated SDK/CLI export edits from other workers, so aggregate catalog verification for this slice should run from the clean staged worktree.
