# LSP Frontend Operation Index

Date: 2026-06-14 21:03 Asia/Shanghai

## Summary

- Added `frontend_operation_ids` to the LSP surface contract using `get_frontend_api_binding_index("lsp")`.
- Aligned LSP with the CLI and MCP static adapter contracts so all three expose stable frontend operation-id slices from the maintained binding index.
- Updated interface and SDK manual text to describe CLI, MCP, and LSP surface-contract mirrors consistently.

## Verification

- `rtk uv run python -m py_compile src/paradev/surfaces/lsp.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/lsp.py`
- `rtk bash scripts/flake.bash --all --paths src/paradev/surfaces/lsp.py tests/test_architecture.py`
- Targeted architecture tests for LSP surface contracts, binding-index helper lookups, and frontend API surface bindings.
- Direct SDK probe for `get_lsp_contract()["frontend_operation_ids"]` parity with `get_frontend_api_binding_index("lsp")`.

## Notes

- This is a behavior-preserving API contract alignment; LSP methods, payload schemas, and runtime server behavior are unchanged.
- Full-suite tests are intentionally skipped to reduce CPU contention while PIHC3 migration work continues in parallel.
