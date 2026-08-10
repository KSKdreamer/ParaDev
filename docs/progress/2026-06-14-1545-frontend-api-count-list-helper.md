# Frontend API Count List Helper

Date: 2026-06-14 15:45 Asia/Shanghai

## Summary

- Reused `_frontend_api_count_list` and `_frontend_api_count_list_cell` across REST, payload, surface, control, input-target, required-input, and form footprint summaries.
- Added an `exclude` option to `_frontend_api_count_list` for the existing payload summary's `untyped` omission.
- Kept emitted count ordering and table content unchanged while removing local list-formatting boilerplate from the SDK-owned frontend API renderer.

## Verification

- Compile check: `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py` completed cleanly.
- Focused contract tests: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_sdk_cli_reference_manual_matches_sdk_renderer tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown tests/test_cli.py::test_frontend_api_cli_outputs_sdk_cli_reference_markdown` passed `4 passed in 1.04s`.
- Path-scoped flake: `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py` completed cleanly with `1 file would be left unchanged`.
- Heaven-style scan: `rtk uv run python /Users/magolor/.agents/skills/heaven-style-0.1.1.1/scripts/scan.py src/paradev/sdk/frontend_api.py` reported `OK: 1 file(s) - no banned imports`.
- Scanner path note: the repo-local `.agents/skills/heaven-style-0.1.1.1/scripts/scan.py` path was unavailable in the shared dirty workspace, so the installed Heaven-style scanner copy was used for this check.

## Notes

- This is a behavior-preserving maintainability slice scoped to `src/paradev/sdk/frontend_api.py`.
- Full-suite tests were intentionally skipped to reduce CPU contention while PIHC3 migration work continues in parallel.
