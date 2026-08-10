# 2026-06-14 12:55 Frontend API Input Index Row Builder

## Focus

- Continue modularizing the SDK-owned frontend API reference renderer.
- Keep input-related API tables stable while sharing the common operation-input row rendering path.

## Changes

- Added `_frontend_api_input_index_rows` for input table row construction.
- Reused it for all-input, required-input, default-input, constraint-input, target-input, and alias-input indexes.
- Added named predicates for required, default, constraint, and alias filters so each table contract remains easy to audit.

## Verification

- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_sdk_cli_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown tests/test_cli.py::test_frontend_api_cli_outputs_sdk_cli_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style-0.1.1.1/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py`

## Notes

- Full-suite tests are deferred to keep CPU available for parallel PIHC2-to-PIHC3 migration work.
- Staging remains limited to `src/paradev/sdk/frontend_api.py` and this progress note; desktop files, PIHC3 migration files, generated frontend assets, skill-directory churn, and `node_modules` are intentionally untouched.
