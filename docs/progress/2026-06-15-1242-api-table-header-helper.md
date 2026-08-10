# 2026-06-15 12:42 API table header helper

## Scope

- Added a shared `table_header(...)` helper for generated Markdown table header/separator rows.
- Routed API standard table headers through the helper in the project, architecture, PDX, LSP, catalog, CLI, REST, MCP, and API catalog reference renderers.
- Reused `api_index_table_header(...)` in the API catalog indexes and removed the redundant local index-row wrapper.
- Kept renderer-owned schema labels explicit at each call site.
- Kept rendered Markdown text and API table payloads unchanged.
- Left unrelated desktop, skill, PIHC3, localization, and logo worktree edits untouched.

## Verification

- Renderer/table comparison against `HEAD` passed for project, architecture, PDX, LSP, catalog, CLI, REST, MCP, and API catalog reference modules.
- `rtk bash scripts/test.bash tests/test_api_table.py ... -q` with the nine affected API-table contract tests: 20 passed.
- `rtk uv run python -m py_compile ...` for the shared helper, touched renderers, and helper tests.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py ...`
- `rtk bash scripts/flake.bash --ci --paths ...`
- Full test suite deferred to reduce CPU while other migration workers are active.

## Git hygiene

- Stage only the shared Markdown helper, touched API reference renderers, helper tests, and this note.
- Do not stage `node_modules/`.
