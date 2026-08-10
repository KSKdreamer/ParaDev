# 2026-06-14 09:41 - Frontend API Option Provider Helper

## Scope

- Added `_frontend_api_option_source_provider_id(...)` in `src/paradev/sdk/frontend_api.py`.
- Routed input field, form control, required input, and input alias tables through the shared option-source provider id helper.
- Preserved public frontend API behavior and generated table columns.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
  - 2 passed in 0.92s.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
  - OK: 1 file(s) - no banned imports.
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py`
  - All done; 1 file would be left unchanged.
