# Frontend API Table Row Helper

Date: 2026-06-14 16:07 Asia/Shanghai

## Summary

- Added a private `_frontend_api_table_rows` helper to centralize conversion from cell rows into markdown table rows.
- Reused the helper across static group summaries, detail-record tables, option-provider tables, input-field tables, and operation form summaries.
- Kept cell builders, row ordering, and emitted frontend API content unchanged.

## Verification

- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_sdk_cli_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown tests/test_cli.py::test_frontend_api_cli_outputs_sdk_cli_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py`

An initial path-scoped flake run reported Black wrapping changes; after applying those formatting updates, the rerun completed cleanly.

## Notes

- This is a behavior-preserving maintainability slice scoped to `src/paradev/sdk/frontend_api.py`.
- Full-suite tests were intentionally skipped to reduce CPU contention while PIHC3 migration work continues in parallel.
