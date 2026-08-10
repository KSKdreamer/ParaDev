# Frontend API REST Cell Rows

Date: 2026-06-14 16:30 Asia/Shanghai

## Summary

- Routed REST static-query, dynamic-query-field, and routed-input tables through `_frontend_api_table_rows`.
- Removed private row wrappers that only converted REST cell builders into Markdown table rows.
- Kept REST table filtering, ordering, route-name resolution, and emitted frontend API Markdown unchanged.

## Verification

- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_sdk_cli_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown tests/test_cli.py::test_frontend_api_cli_outputs_sdk_cli_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py`

## Notes

- This is a behavior-preserving maintainability slice scoped to `src/paradev/sdk/frontend_api.py`.
- Full-suite tests were intentionally skipped to reduce CPU contention while PIHC3 migration work continues in parallel.
