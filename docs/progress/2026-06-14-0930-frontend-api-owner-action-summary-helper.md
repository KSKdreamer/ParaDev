# 2026-06-14 09:30 - Frontend API Owner Action Summary Helper

## Scope

- Added `_frontend_api_owner_action_summary_rows(...)` in `src/paradev/sdk/frontend_api.py`.
- Routed group/workspace execution summaries and group/workspace confirmation summaries through the shared owner/action row renderer.
- Kept public frontend API behavior and rendered table column shapes unchanged.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
  - 2 passed in 0.88s.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
  - OK: 1 file(s) - no banned imports.
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py`
  - All done; 1 file would be left unchanged.
