# 2026-06-14 13:36 Frontend API Binding Input Row

## Focus

- Continue modularizing the SDK-owned frontend API reference renderer.
- Keep SDK, CLI, MCP, and LSP binding input API tables stable while separating row assembly from cell assembly.

## Changes

- Added `_frontend_api_binding_input_row`.
- Updated `_frontend_api_binding_input_index_rows` to delegate per-input table-row rendering to the helper.
- Preserved operation order, binding lookup behavior, input order, rendered columns, and markdown output for all binding input tables.

## Verification

- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_sdk_cli_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown tests/test_cli.py::test_frontend_api_cli_outputs_sdk_cli_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style-0.1.1.1/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py`

## Notes

- Full-suite tests are deferred to keep CPU available for parallel PIHC2-to-PIHC3 migration work.
- Staging remains limited to `src/paradev/sdk/frontend_api.py` and this progress note; desktop files, PIHC3 migration files, generated frontend assets, skill-directory churn, and `node_modules` are intentionally untouched.
