# Frontend API Binding Helper Refactor

## Scope

- Continued the behavior-preserving frontend API renderer cleanup stream.
- Added `_frontend_api_operation_bindings` as the shared binding Mapping guard.
- Routed surface counts, REST operation discovery, binding input rows, and group/workspace binding summaries through shared binding helpers.
- Collapsed group and workspace-section binding summary row builders onto `_frontend_api_binding_summary_cells`.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`

## Notes

- Full-suite tests were intentionally skipped to keep CPU available for parallel PIHC2-to-PIHC3 migration work.
- No PIHC migration files were edited in this slice.
