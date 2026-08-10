# Frontend API Surface Binding Index

Date: 2026-06-14 21:13 Asia/Shanghai

## Summary

- Split surface coverage and reverse binding index population out of `_frontend_api_index`.
- Kept unbound-row handling, callable surface coverage buckets, REST/CLI/MCP/LSP/SDK binding keys, and operation id ordering unchanged.
- Preserved the SDK-owned frontend API contract and rendered API table behavior.

## Verification

- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --all --paths src/paradev/sdk/frontend_api.py`
- Targeted frontend API architecture index test and CLI binding lookup test that avoid the concurrently dirty desktop generated files.
- Surface/binding index probe and renderer digest check for `render_frontend_api_reference_markdown`, `render_frontend_api_sdk_cli_markdown`, and `render_frontend_api_typescript`.

## Notes

- This is a behavior-preserving maintainability refactor inside the SDK-owned frontend API index builder.
- Full-suite tests are intentionally skipped to reduce CPU contention while PIHC3 migration work continues in parallel.
- Concurrent desktop TypeScript/generated, PIHC3 migration, logo, and skill files were left untouched.
