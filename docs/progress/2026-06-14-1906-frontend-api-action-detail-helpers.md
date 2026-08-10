# Frontend API Action Detail Helpers

Date: 2026-06-14 19:06 Asia/Shanghai

## Summary

- Split `get_frontend_api_action` into focused private helpers for workspace action lookup, optional form lookup, and final action-detail payload assembly.
- Kept action-detail schema names, section lists, bindings, execution hints, form payloads, option-field ordering, and option-source payloads unchanged.
- Left generated frontend API Markdown and TypeScript contracts behavior-preserving.

## Verification

- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --all --paths src/paradev/sdk/frontend_api.py`
- Targeted frontend API action-detail, form, renderer parity, REST route, and CLI tests.
- Renderer digest check for `render_frontend_api_reference_markdown`, `render_frontend_api_sdk_cli_markdown`, and `render_frontend_api_typescript`.

## Notes

- This is a maintainability-only refactor scoped to SDK-owned frontend action-detail construction.
- Full-suite tests are intentionally skipped to reduce CPU contention while PIHC3 migration work continues in parallel.
