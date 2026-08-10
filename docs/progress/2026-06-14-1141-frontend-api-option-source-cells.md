# 2026-06-14 11:41 - Frontend API Option Source Cells

## Focus

- Continued the frontend API reference renderer cleanup for SDK-owned dynamic option-source tables.
- Kept the slice isolated from PIHC3 migration, desktop UI, generated frontend assets, and manual edits already present in the shared worktree.

## Changes

- Added `_frontend_api_option_source_cells(...)` in `src/paradev/sdk/frontend_api.py`.
- Routed option source index row generation through the helper so operation id, field name, values path, provider operation, requirements, forwarded fields, and fixed filters stay in one row builder.
- Preserved existing filtering: rows are emitted only for input fields whose `option_source` metadata is a mapping.

## Verification

- Passed: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_sdk_cli_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown tests/test_cli.py::test_frontend_api_cli_outputs_sdk_cli_reference_markdown`
- Passed: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- Passed: `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py`

## Notes

- Full-suite tests intentionally deferred to reduce CPU contention.
- `node_modules` remains excluded from staging.
