# Frontend API Binding Lookup Payload

Date: 2026-06-14 19:39 Asia/Shanghai

## Summary

- Split `get_frontend_api_binding_lookup` into a private payload helper for the JSON-safe binding reverse-lookup response.
- Preserved supported-surface validation, unknown-key empty-list behavior, operation id ordering, and response shape.
- Kept generated frontend API Markdown and TypeScript contracts behavior-preserving.

## Verification

- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --all --paths src/paradev/sdk/frontend_api.py`
- Targeted frontend API binding lookup, REST route, renderer parity, and CLI binding tests.
- Direct SDK probe for matched and missing binding lookup payloads.
- Renderer digest check for `render_frontend_api_reference_markdown`, `render_frontend_api_sdk_cli_markdown`, and `render_frontend_api_typescript`.

## Notes

- This is a maintainability-only refactor inside the SDK-owned binding reverse-lookup payload path.
- Full-suite tests are intentionally skipped to reduce CPU contention while PIHC3 migration work continues in parallel.
