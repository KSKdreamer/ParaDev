# Frontend API Group Slice Helpers

Date: 2026-06-14 19:11 Asia/Shanghai

## Summary

- Split `get_frontend_api_group` into focused private helpers for group row lookup, group operation filtering, and final group payload assembly.
- Kept group metadata copy behavior, operation id ordering, operation rows, scoped indexes, and unknown-group errors unchanged.
- Left generated frontend API Markdown and TypeScript contracts behavior-preserving.

## Verification

- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --all --paths src/paradev/sdk/frontend_api.py`
- Targeted frontend API lookup, group selector, renderer parity, REST selector, and CLI tests.
- Renderer digest check for `render_frontend_api_reference_markdown`, `render_frontend_api_sdk_cli_markdown`, and `render_frontend_api_typescript`.

## Notes

- This is a maintainability-only refactor scoped to SDK-owned frontend API group slice construction.
- Full-suite tests are intentionally skipped to reduce CPU contention while PIHC3 migration work continues in parallel.
