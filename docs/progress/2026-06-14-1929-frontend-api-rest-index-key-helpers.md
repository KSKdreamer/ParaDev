# Frontend API REST Index Key Helpers

Date: 2026-06-14 19:29 Asia/Shanghai

## Summary

- Split REST reverse-index key construction into private helpers for the binding payload and query normalization.
- Preserved the public `build_frontend_api_rest_index_key` API, sorted query key behavior, ignored `None` query values, and downstream REST binding lookup behavior.
- Kept generated frontend API Markdown and TypeScript contracts behavior-preserving.

## Verification

- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --all --paths src/paradev/sdk/frontend_api.py`
- Targeted frontend API REST key, binding/index helper, REST binding route, renderer parity, and CLI binding tests.
- Direct REST-key probe for sorted booleans, ignored `None`, and empty-query keys.
- Renderer digest check for `render_frontend_api_reference_markdown`, `render_frontend_api_sdk_cli_markdown`, and `render_frontend_api_typescript`.

## Notes

- This is a maintainability-only refactor inside the SDK-owned REST reverse-index lookup path.
- Full-suite tests are intentionally skipped to reduce CPU contention while PIHC3 migration work continues in parallel.
