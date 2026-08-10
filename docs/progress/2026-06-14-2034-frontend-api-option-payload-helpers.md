# Frontend API Option Payload Helpers

Date: 2026-06-14 20:34 Asia/Shanghai

## Summary

- Split resolved dynamic option payload mutation into provider-schema and option-row helpers.
- Preserved the `resolve_frontend_api_options(...)` payload shape, provider schema propagation, option row order, count calculation, and missing-requirement behavior.
- Kept the SDK-owned frontend API contract unchanged for CLI, REST, generated TypeScript, and GUI consumers.

## Verification

- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --all --paths src/paradev/sdk/frontend_api.py`
- Targeted frontend API option resolver, REST options route, CLI option-field, input normalization, renderer parity, and TypeScript renderer tests.
- Direct SDK probe for available options, missing requirements, and fields without `option_source`.
- Renderer digest check for `render_frontend_api_reference_markdown`, `render_frontend_api_sdk_cli_markdown`, and `render_frontend_api_typescript`.

## Notes

- This is a behavior-preserving maintainability refactor inside the SDK-owned dynamic option payload builder.
- Full-suite tests are intentionally skipped to reduce CPU contention while PIHC3 migration work continues in parallel.
