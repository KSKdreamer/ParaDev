# 2026-06-14 09:26 - Frontend API Confirmation Summary Helper

## Scope

- Added `_frontend_api_confirmation_counts(...)` in `src/paradev/sdk/frontend_api.py`.
- Routed group and workspace-section confirmation summary tables through the shared confirmation counting helper.
- Kept the public frontend API contract and rendered table shapes unchanged.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown`
  - 2 passed in 1.01s.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
  - OK: 1 file(s) - no banned imports.
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py`
  - All done; 1 file would be left unchanged.
