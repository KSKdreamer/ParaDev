# Frontend API Index Map Helpers

Date: 2026-06-14 19:19 Asia/Shanghai

## Summary

- Added private frontend API helpers for operation-id sequence checks, copied operation-id lists, copied operation-id indexes, and contract index-map lookup.
- Routed group operation-id lists, status/mode/workspace/payload index selectors, and binding index copies through the shared helpers.
- Preserved public SDK API names, REST/CLI/MCP binding behavior, unknown-key behavior, and generated frontend API contract output.

## Verification

- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --all --paths src/paradev/sdk/frontend_api.py`
- Targeted frontend API binding/index helper, renderer parity, REST binding lookup, MCP/CLI surface contract, and CLI selector tests.
- Renderer digest check for `render_frontend_api_reference_markdown`, `render_frontend_api_sdk_cli_markdown`, and `render_frontend_api_typescript`.

## Notes

- This is a maintainability-only refactor inside the SDK-owned frontend API lookup layer.
- Full-suite tests are intentionally skipped to reduce CPU contention while PIHC3 migration work continues in parallel.
