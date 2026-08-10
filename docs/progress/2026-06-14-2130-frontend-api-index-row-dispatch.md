# Frontend API Index Row Dispatch

Date: 2026-06-14 21:30 Asia/Shanghai

## Summary

- Split per-operation frontend API index population out of `_frontend_api_index`.
- Kept primary, payload, read/write mode, surface coverage, and binding reverse-index updates in the same order.
- Preserved generated frontend API contract shape and rendered API table behavior.

## Verification

- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --all --paths src/paradev/sdk/frontend_api.py`
- Targeted frontend API architecture and CLI contract tests that avoid the concurrently dirty desktop generated files.
- Index-row probe and renderer digest check for `render_frontend_api_reference_markdown`, `render_frontend_api_sdk_cli_markdown`, and `render_frontend_api_typescript`.

## Notes

- This is a behavior-preserving maintainability refactor inside the SDK-owned frontend API index builder.
- Full-suite tests are intentionally skipped to reduce CPU contention while PIHC3 migration work continues in parallel.
- Existing dirty desktop TypeScript/generated files, PIHC3 progress notes, and `node_modules/` were left untouched.
