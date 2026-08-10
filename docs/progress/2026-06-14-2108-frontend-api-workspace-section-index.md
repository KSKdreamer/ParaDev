# Frontend API Workspace Section Index

Date: 2026-06-14 21:08 Asia/Shanghai

## Summary

- Split workspace-section source-index lookup out of `_frontend_api_workspace_section_index`.
- Reused the shared frontend operation-id sequence/list helpers instead of duplicating validation and string conversion in the workspace index builder.
- Preserved workspace-section index keys, operation id ordering, generated contract shape, and rendered API table behavior.

## Verification

- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --all --paths src/paradev/sdk/frontend_api.py`
- Targeted frontend API architecture and CLI contract tests that do not depend on the concurrently dirty desktop TypeScript files.
- Renderer digest check for `render_frontend_api_reference_markdown`, `render_frontend_api_sdk_cli_markdown`, and `render_frontend_api_typescript`.

## Notes

- This is a behavior-preserving maintainability refactor inside the SDK-owned frontend API index builder.
- Full-suite tests are intentionally skipped to reduce CPU contention while PIHC3 migration work continues in parallel.
- Existing uncommitted desktop TypeScript/generated changes were left untouched and unstaged.
