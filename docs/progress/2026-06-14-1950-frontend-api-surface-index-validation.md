# Frontend API Surface Index Validation

Date: 2026-06-14 19:50 Asia/Shanghai

## Summary

- Centralized frontend surface index choices in a private SDK constant.
- Split callable-surface validation out of `get_frontend_api_surface_operation_ids`.
- Preserved supported-surface error text, surface operation id lookup behavior, and generated frontend API contract outputs.

## Verification

- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --all --paths src/paradev/sdk/frontend_api.py`
- Targeted frontend API binding lookup, surface index, renderer parity, and CLI binding tests.
- Direct SDK probe for supported, unbound, and unsupported surface operation id lookups.
- Renderer digest check for `render_frontend_api_reference_markdown`, `render_frontend_api_sdk_cli_markdown`, and `render_frontend_api_typescript`.

## Notes

- This is a maintainability-only refactor inside the SDK-owned frontend API index helper layer.
- Full-suite tests are intentionally skipped to reduce CPU contention while PIHC3 migration work continues in parallel.
