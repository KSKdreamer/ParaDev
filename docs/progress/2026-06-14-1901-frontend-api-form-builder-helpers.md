# Frontend API Form Builder Helpers

Date: 2026-06-14 19:01 Asia/Shanghai

## Summary

- Split `get_frontend_api_form` into focused private helpers for field projection, required-name extraction, defaults, aliases, JSON Schema construction, and final payload assembly.
- Kept form schema names, field ordering, defaults, aliases, mutation flags, JSON Schema shape, and operation payloads unchanged.
- Left generated frontend API Markdown and TypeScript contracts behavior-preserving.

## Verification

- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --all --paths src/paradev/sdk/frontend_api.py`
- Targeted frontend API form, normalizer, renderer parity, and CLI tests.
- Renderer digest check for `render_frontend_api_reference_markdown`, `render_frontend_api_sdk_cli_markdown`, and `render_frontend_api_typescript`.

## Notes

- This is a maintainability-only refactor scoped to SDK-owned frontend form contract construction.
- Full-suite tests are intentionally skipped to reduce CPU contention while PIHC3 migration work continues in parallel.
