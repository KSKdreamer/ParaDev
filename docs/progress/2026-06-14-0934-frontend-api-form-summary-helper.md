# 2026-06-14 09:34 - Frontend API Form Summary Helper

## Scope

- Added `_frontend_api_owner_operation_detail_rows(...)` and `_frontend_api_form_summary_cells(...)` in `src/paradev/sdk/frontend_api.py`.
- Routed workspace-section and group form summary tables through the shared owner/form row renderer.
- Preserved public frontend API behavior and generated table shapes.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
  - 2 passed in 0.90s.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
  - OK: 1 file(s) - no banned imports.
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py`
  - All done; 1 file would be left unchanged.
