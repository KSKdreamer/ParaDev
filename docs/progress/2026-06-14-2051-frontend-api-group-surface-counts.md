# Frontend API Group Surface Counts

Date: 2026-06-14 20:51 Asia/Shanghai

## Summary

- Split group bucketing out of `_frontend_api_group_surface_counts`.
- Preserved per-group surface count keys, group iteration order, empty-group behavior, summary payload shape, and rendered API table output.
- Kept SDK, CLI, REST, MCP, LSP, TypeScript, and GUI-facing frontend API summaries behavior-preserving.

## Verification

- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --all --paths src/paradev/sdk/frontend_api.py`
- Targeted frontend API summary, renderer parity, SDK CLI reference, TypeScript renderer, and CLI contract tests.
- Renderer digest check for `render_frontend_api_reference_markdown`, `render_frontend_api_sdk_cli_markdown`, and `render_frontend_api_typescript`.

## Notes

- This is a behavior-preserving maintainability refactor inside the SDK-owned frontend API summary/table generation path.
- Full-suite tests are intentionally skipped to reduce CPU contention while PIHC3 migration work continues in parallel.
