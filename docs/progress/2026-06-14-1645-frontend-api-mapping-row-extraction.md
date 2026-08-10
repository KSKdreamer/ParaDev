# Frontend API Mapping Row Extraction

Date: 2026-06-14 16:45 Asia/Shanghai

## Summary

- Added shared frontend API helpers for extracting mapping rows from sequence-like contract values and dict-copying rows that need local mutation safety.
- Routed API summary, group, workspace section, operation, input, and workspace action row builders through the shared extraction helpers.
- Kept generated frontend API contract ordering, filtering, and Markdown row emission behavior unchanged.

## Verification

- `rtk bash scripts/flake.bash --all --paths src/paradev/sdk/frontend_api.py`
- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_sdk_cli_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown tests/test_cli.py::test_frontend_api_cli_outputs_sdk_cli_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py`

## Notes

- This is a behavior-preserving maintainability slice scoped to frontend API reference row construction.
- Full-suite tests were intentionally skipped to reduce CPU contention while PIHC3 migration work continues in parallel.
