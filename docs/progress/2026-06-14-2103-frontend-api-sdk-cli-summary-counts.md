# Frontend API SDK CLI Summary Counts

Date: 2026-06-14 21:03 Asia/Shanghai

## Summary

- Split SDK CLI summary count-map validation out of `_frontend_api_sdk_cli_summary_rows`.
- Preserved invalid-contract handling, missing summary handling, group iteration order, SDK/CLI summary cells, and rendered frontend API SDK CLI tables.
- Kept SDK, CLI, REST, MCP, LSP, TypeScript, and GUI-facing frontend API contracts behavior-preserving.

## Verification

- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --all --paths src/paradev/sdk/frontend_api.py`
- Targeted frontend API summary, renderer parity, SDK CLI reference, TypeScript renderer, and CLI contract tests.
- Renderer digest check for `render_frontend_api_reference_markdown`, `render_frontend_api_sdk_cli_markdown`, and `render_frontend_api_typescript`.

## Notes

- This is a behavior-preserving maintainability refactor inside the SDK-owned frontend API SDK CLI summary renderer.
- Full-suite tests are intentionally skipped to reduce CPU contention while PIHC3 migration work continues in parallel.
