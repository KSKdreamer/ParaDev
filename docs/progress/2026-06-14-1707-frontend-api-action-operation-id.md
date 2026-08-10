# Frontend API Action Operation IDs

Date: 2026-06-14 17:07 Asia/Shanghai

## Summary

- Added `_frontend_api_action_operation_id` to centralize workspace action operation-id extraction.
- Routed workspace section action lookup, workspace action group aggregation, action execution rows, and confirmation rows through the helper.
- Kept action filtering, row ordering, and generated API Markdown/TypeScript behavior unchanged.

## Verification

- `rtk bash scripts/flake.bash --all --paths src/paradev/sdk/frontend_api.py`
- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_sdk_cli_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_typescript_renderer_matches_desktop_contract_file tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown tests/test_cli.py::test_frontend_api_cli_outputs_sdk_cli_reference_markdown tests/test_cli.py::test_frontend_api_cli_outputs_typescript_contract`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py`

## Notes

- This is a behavior-preserving maintainability slice scoped to frontend API workspace action operation-id rendering and lookup.
- Full-suite tests were intentionally skipped to reduce CPU contention while PIHC3 migration work continues in parallel.
