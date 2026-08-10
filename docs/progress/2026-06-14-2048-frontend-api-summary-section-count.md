# Frontend API Summary Section Count

Date: 2026-06-14 20:48 Asia/Shanghai

## Summary

- Split frontend API workspace section counting into `_frontend_api_workspace_section_count`.
- Preserved the summary payload shape and the existing rule that non-sequence, string, and bytes `sections` values count as zero.
- Kept the SDK-owned frontend API summary contract unchanged for API table, CLI, REST, and GUI consumers.

## Verification

- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --all --paths src/paradev/sdk/frontend_api.py`
- Targeted frontend API contract summary, reference renderer, CLI API table, and TypeScript renderer tests.
- Direct SDK probe for `workspace_section_count` in the frontend API contract.
- Renderer digest check for `render_frontend_api_reference_markdown`, `render_frontend_api_sdk_cli_markdown`, and `render_frontend_api_typescript`.

## Notes

- This is a behavior-preserving maintainability refactor inside the frontend API summary/table contract path.
- Full-suite tests are intentionally skipped to reduce CPU contention while PIHC3 migration work continues in parallel.
