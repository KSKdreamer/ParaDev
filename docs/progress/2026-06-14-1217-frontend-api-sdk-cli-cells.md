# 2026-06-14 12:17 - Frontend API SDK CLI Cells

## Focus

- Continued the frontend API reference renderer cleanup around the compact SDK/CLI API reference table.
- Kept the slice isolated from PIHC3 migration, desktop UI, generated frontend assets, and existing manual edits in the shared worktree.

## Changes

- Added `_frontend_api_sdk_cli_cells(...)` in `src/paradev/sdk/frontend_api.py`.
- Routed compact SDK/CLI row generation through the helper so operation identity, mutability, SDK binding, CLI binding, inputs, and summary cells are built in one named row builder.
- Preserved the existing SDK/CLI reference table column order and row rendering behavior.

## Verification

- Passed: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_sdk_cli_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown tests/test_cli.py::test_frontend_api_cli_outputs_sdk_cli_reference_markdown`
- Passed: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- Passed: `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py`

## Notes

- Full-suite tests intentionally deferred to reduce CPU contention.
- `node_modules` remains excluded from staging.
