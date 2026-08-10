# Frontend API Surface Cell Helper

Date: 2026-06-14 17:34 Asia/Shanghai

## Summary

- Added `_frontend_api_operation_surface_cells` for SDK/CLI/REST/MCP/LSP reference-table cell rendering.
- Routed the full frontend API reference table and compact SDK/CLI table through the helper.
- Kept operation row data and generated table behavior unchanged.

## Verification

- `rtk bash scripts/flake.bash --all --paths src/paradev/sdk/frontend_api.py`
- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_sdk_cli_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_typescript_renderer_matches_desktop_contract_file tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown tests/test_cli.py::test_frontend_api_cli_outputs_sdk_cli_reference_markdown tests/test_cli.py::test_frontend_api_cli_outputs_typescript_contract`

## Notes

- This is a behavior-preserving maintainability slice scoped to frontend API Markdown surface-cell rendering.
- Full-suite tests were intentionally skipped to reduce CPU contention while PIHC3 migration work continues in parallel.
