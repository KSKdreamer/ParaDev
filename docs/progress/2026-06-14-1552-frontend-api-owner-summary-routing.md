# Frontend API Owner Summary Routing

Date: 2026-06-14 15:52 Asia/Shanghai

## Summary

- Added private workspace-section and group operation-summary routing helpers in the SDK-owned frontend API renderer.
- Replaced repeated direct `_frontend_api_owner_operation_summary_rows(...)` calls across REST, binding, mode/status, payload, control, option-source, input-target, validation, default, required, and alias summary tables.
- Kept table row generation, operation grouping, and emitted frontend API content unchanged.

## Verification

- Compile check: `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py` completed cleanly.
- Focused contract tests: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_sdk_cli_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown tests/test_cli.py::test_frontend_api_cli_outputs_sdk_cli_reference_markdown` passed `4 passed in 1.02s`.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py` reported `OK: 1 file(s) - no banned imports`.
- Path-scoped flake: `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py` completed cleanly with `1 file would be left unchanged`.

## Notes

- This is a behavior-preserving maintainability slice scoped to `src/paradev/sdk/frontend_api.py`.
- Full-suite tests were intentionally skipped to reduce CPU contention while PIHC3 migration work continues in parallel.
