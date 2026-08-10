# Frontend API Option Provider Forwarding

Date: 2026-06-14 20:30 Asia/Shanghai

## Summary

- Split option-source forwarded value insertion out of `_frontend_api_option_provider_values`.
- Preserved filter precedence over forwarded values, ignored missing or `None` forwarded values, provider value ordering, option payloads, and provider execution behavior.
- Kept SDK, CLI, REST options endpoint, and generated frontend API contract outputs behavior-preserving.

## Verification

- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --all --paths src/paradev/sdk/frontend_api.py`
- Targeted frontend API option resolver, REST options route, CLI option-field, renderer parity, and TypeScript renderer tests.
- Direct SDK probe for provider filter defaults, forwarded values, missing requirements, and fields without `option_source`.
- Renderer digest check for `render_frontend_api_reference_markdown`, `render_frontend_api_sdk_cli_markdown`, and `render_frontend_api_typescript`.

## Notes

- This is a maintainability-only refactor inside the SDK-owned dynamic option resolver path.
- Full-suite tests are intentionally skipped to reduce CPU contention while PIHC3 migration work continues in parallel.
