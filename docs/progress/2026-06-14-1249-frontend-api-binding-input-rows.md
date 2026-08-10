# 2026-06-14 12:49 Frontend API Binding Input Rows

## Focus

- Continue modularizing the SDK-owned frontend API reference renderer.
- Keep binding-input API tables stable while separating row-source traversal from markdown table-row construction.

## Changes

- Added `_frontend_api_binding_input_rows` to collect operation, binding, and field triples for a selected surface.
- Reused that row source from `_frontend_api_binding_input_index_rows`.
- Preserved operation order, surface binding checks, input field order, and all existing binding-input table cells.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_sdk_cli_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown tests/test_cli.py::test_frontend_api_cli_outputs_sdk_cli_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style-0.1.1.1/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py`

## Notes

- Full-suite tests are deferred to keep CPU available for parallel PIHC2-to-PIHC3 migration work.
- Staging remains limited to `src/paradev/sdk/frontend_api.py` and this progress note; desktop files, PIHC3 migration files, generated frontend assets, skill-directory churn, and `node_modules` are intentionally untouched.
