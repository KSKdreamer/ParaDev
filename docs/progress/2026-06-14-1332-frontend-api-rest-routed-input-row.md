# 2026-06-14 13:32 Frontend API REST Routed Input Row

## Focus

- Continue modularizing the SDK-owned frontend API reference renderer.
- Keep REST path-parameter and body-field API tables stable while separating shared row assembly from cell assembly.

## Changes

- Added `_frontend_api_rest_routed_input_row`.
- Updated `_frontend_api_rest_routed_input_index_rows` to delegate per-field table-row rendering to the helper.
- Preserved REST operation order, routed-name filtering, input order, path-parameter rows, body-field rows, and rendered markdown output.

## Verification

- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_sdk_cli_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown tests/test_cli.py::test_frontend_api_cli_outputs_sdk_cli_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style-0.1.1.1/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py`

## Notes

- Full-suite tests are deferred to keep CPU available for parallel PIHC2-to-PIHC3 migration work.
- Staging remains limited to `src/paradev/sdk/frontend_api.py` and this progress note; desktop files, PIHC3 migration files, generated frontend assets, skill-directory churn, and `node_modules` are intentionally untouched.
