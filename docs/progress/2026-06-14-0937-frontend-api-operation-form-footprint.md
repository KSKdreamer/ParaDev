# 2026-06-14 09:37 - Frontend API Operation Form Footprint

## Scope

- Extended `_frontend_api_form_footprint(...)` with `control_names` for operation-level form summaries.
- Routed `_frontend_api_operation_form_summary_index_rows(...)` through the shared form footprint instead of recomputing input/default/alias/constraint counts inline.
- Kept public frontend API behavior and generated table columns unchanged.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
  - 2 passed in 0.91s.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
  - OK: 1 file(s) - no banned imports.
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py`
  - All done; 1 file would be left unchanged.
