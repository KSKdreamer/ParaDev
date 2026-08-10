# 2026-06-14 12:31 - Frontend API Group Index Row

## Focus

- Continued the frontend API reference renderer cleanup around generated index tables.
- Kept the slice isolated from PIHC3 migration, desktop UI, generated frontend assets, and existing manual edits in the shared worktree.

## Changes

- Added `_frontend_api_group_index_row(...)` in `src/paradev/sdk/frontend_api.py`.
- Routed group index row generation through the helper so group id, title, operation count, and operation ids stay behind one named row builder.
- Preserved the existing group filtering, group ordering, and operation-id detail rendering.

## Verification

- Passed: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_sdk_cli_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown tests/test_cli.py::test_frontend_api_cli_outputs_sdk_cli_reference_markdown`
- Passed: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- Passed: `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py`

## Notes

- Full-suite tests intentionally deferred to reduce CPU contention.
- `node_modules` remains excluded from staging.
