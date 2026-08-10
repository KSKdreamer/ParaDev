# Frontend API Owner Row Rendering

Date: 2026-06-14 16:14 Asia/Shanghai

## Summary

- Routed owner operation summary, owner operation detail, and owner action summary tables through `_frontend_api_table_rows`.
- Removed private single-row wrapper functions that only delegated to cell builders and `_frontend_api_table_row`.
- Kept owner row ordering, owner-id conversion, cell builders, and emitted frontend API Markdown unchanged.

## Verification

- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_sdk_cli_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown tests/test_cli.py::test_frontend_api_cli_outputs_sdk_cli_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py`

An initial path-scoped flake run reported Black wrapping changes; after applying those formatting updates, the rerun completed cleanly.

## Notes

- This is a behavior-preserving maintainability slice scoped to `src/paradev/sdk/frontend_api.py`.
- Full-suite tests were intentionally skipped to reduce CPU contention while PIHC3 migration work continues in parallel.
