# Frontend API Option Row Helpers

Date: 2026-06-14 20:38 Asia/Shanghai

## Summary

- Split dynamic option row construction out of `_frontend_api_option_rows`.
- Preserved option row filtering, duplicate suppression by `repr(value)`, label fallback, row copying, details extraction, row order, and count behavior.
- Kept the SDK-owned frontend API option payload contract unchanged for CLI, REST, generated TypeScript, and GUI consumers.

## Verification

- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --all --paths src/paradev/sdk/frontend_api.py`
- Targeted frontend API option resolver, REST options route, CLI option-field, input normalization, renderer parity, and TypeScript renderer tests.
- Direct SDK probe for available options, missing requirements, and fields without `option_source`.
- Renderer digest check for `render_frontend_api_reference_markdown`, `render_frontend_api_sdk_cli_markdown`, and `render_frontend_api_typescript`.

## Notes

- This is a behavior-preserving maintainability refactor inside the SDK-owned dynamic option payload path.
- Full-suite tests are intentionally skipped to reduce CPU contention while PIHC3 migration work continues in parallel.
