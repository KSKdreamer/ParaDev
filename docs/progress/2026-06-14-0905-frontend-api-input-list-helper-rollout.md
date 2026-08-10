# Frontend API Input List Helper Rollout

## Scope

- Continued the behavior-preserving frontend API renderer cleanup stream.
- Added `_frontend_api_input_rows` as the shared input-list validator for operation rows.
- Routed REST summary/dynamic-query/routed-input builders, binding input rows, and operation form summary rows through the helper.
- Left REST-bound operation discovery for a later slice because it has separate route-key behavior.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py tests/test_architecture.py tests/test_cli.py`

## Notes

- Full-suite tests were intentionally skipped to keep CPU available for parallel PIHC2-to-PIHC3 migration work.
- No PIHC migration files were edited in this slice.
