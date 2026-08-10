# Frontend API Static Summary Counts

Date: 2026-06-14 20:57 Asia/Shanghai

## Summary

- Split static group summary count lookup out of `_frontend_api_static_group_summary_rows`.
- Preserved invalid-summary handling, missing summary-key handling, group iteration order, markdown cells, and rendered frontend API reference tables.
- Kept SDK, CLI, REST, MCP, LSP, TypeScript, and GUI-facing frontend API summary documentation behavior-preserving.

## Verification

- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --all --paths src/paradev/sdk/frontend_api.py`
- Targeted frontend API summary, renderer parity, SDK CLI reference, TypeScript renderer, and CLI contract tests.
- Renderer digest check for `render_frontend_api_reference_markdown`, `render_frontend_api_sdk_cli_markdown`, and `render_frontend_api_typescript`.

## Notes

- This is a behavior-preserving maintainability refactor inside the SDK-owned frontend API summary table renderer.
- Full-suite tests are intentionally skipped to reduce CPU contention while PIHC3 migration work continues in parallel.
