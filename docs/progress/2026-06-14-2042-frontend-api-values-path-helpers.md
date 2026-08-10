# Frontend API Option Provider Path Helpers

Date: 2026-06-14 20:42 Asia/Shanghai

## Summary

- Split dynamic option provider input preparation out of provider execution.
- Split provider `values_path` traversal into path-value, step, and list-validation helpers.
- Preserved provider normalization errors, project loading, missing-path and non-list error messages, path label formatting, provider row extraction, option row order, and resolved option payload shape.
- Kept the SDK-owned frontend API contract unchanged for CLI, REST, generated TypeScript, and GUI consumers.

## Verification

- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --all --paths src/paradev/sdk/frontend_api.py`
- Targeted frontend API option resolver, REST options route, CLI option-field, input normalization, renderer parity, and TypeScript renderer tests.
- Direct SDK probe for available options, missing requirements, and fields without `option_source`.
- Renderer digest check for `render_frontend_api_reference_markdown`, `render_frontend_api_sdk_cli_markdown`, and `render_frontend_api_typescript`.

## Notes

- This is a behavior-preserving maintainability refactor inside the SDK-owned dynamic option provider path.
- Full-suite tests are intentionally skipped to reduce CPU contention while PIHC3 migration work continues in parallel.
