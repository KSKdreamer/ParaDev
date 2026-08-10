# Frontend API Validation Helpers

Date: 2026-06-14 19:25 Asia/Shanghai

## Summary

- Added private helpers for frontend API choice rendering and `ValueError` construction across operation, group, index, binding-surface, and surface selectors.
- Preserved existing public SDK APIs, exception text, exception chaining for operation/group lookups, unknown-key handling, and generated contract output.
- Kept the refactor scoped to SDK-owned frontend API lookup validation so it does not overlap with PIHC3 migration work.

## Verification

- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --all --paths src/paradev/sdk/frontend_api.py`
- Targeted frontend API lookup, binding/index helper, REST binding lookup, renderer parity, and CLI selector tests.
- Direct error-message probe for unknown operation/group/status/mode/workspace section and unsupported binding/surface values.
- Renderer digest check for `render_frontend_api_reference_markdown`, `render_frontend_api_sdk_cli_markdown`, and `render_frontend_api_typescript`.

## Notes

- This is a maintainability-only refactor inside the SDK-owned frontend API validation layer.
- Full-suite tests are intentionally skipped to reduce CPU contention while PIHC3 migration work continues in parallel.
