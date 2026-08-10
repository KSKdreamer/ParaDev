# Frontend API Operation ID Row Cells

Date: 2026-06-14 16:23 Asia/Shanghai

## Summary

- Added `_frontend_api_operation_id_detail_cells` to centralize the operation-id count/list cell pattern used by API index tables.
- Routed group, status, mode, surface, payload, REST route, binding-surface, and binding lookup index rows through `_frontend_api_table_rows`.
- Removed private row wrappers that only joined operation-id detail cells into Markdown table rows.

## Verification

- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_sdk_cli_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown tests/test_cli.py::test_frontend_api_cli_outputs_sdk_cli_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py`

An initial path-scoped flake run reported one Black wrapping change; after applying that formatting update, the rerun completed cleanly.

## Notes

- This is a behavior-preserving maintainability slice scoped to `src/paradev/sdk/frontend_api.py`.
- Full-suite tests were intentionally skipped to reduce CPU contention while PIHC3 migration work continues in parallel.
