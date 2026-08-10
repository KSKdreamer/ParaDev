# Frontend API Operation Row Helpers

Date: 2026-06-14 19:34 Asia/Shanghai

## Summary

- Split `get_frontend_api_operation` into private helpers for operation-row indexing and operation-row lookup.
- Preserved copied operation row behavior, unknown-operation error text, and exception chaining.
- Kept generated frontend API Markdown and TypeScript contracts behavior-preserving.

## Verification

- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --all --paths src/paradev/sdk/frontend_api.py`
- Targeted frontend API operation lookup, action/form/rest planner, renderer parity, and CLI selector tests.
- Direct SDK probe for copied row mutation isolation and unknown-operation errors.
- Renderer digest check for `render_frontend_api_reference_markdown`, `render_frontend_api_sdk_cli_markdown`, and `render_frontend_api_typescript`.

## Notes

- This is a maintainability-only refactor inside the SDK-owned operation lookup path.
- Full-suite tests are intentionally skipped to reduce CPU contention while PIHC3 migration work continues in parallel.
