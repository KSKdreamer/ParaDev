# 2026-06-15 12:56 API field header helper

## Scope

- Added `api_field_label(...)` and `api_field_table_header(...)` for generated API standard-table headers.
- Added local private standard-field tuples for project, architecture, PDX, LSP, catalog, CLI, REST, MCP, and API catalog references.
- Routed each affected renderer so the same field tuple drives its standard-table header and row rendering.
- Preserved each renderer's field order, list-valued columns, plain Markdown columns, rendered Markdown text, and API table payloads.
- Left unrelated desktop, skill, PIHC3, localization, and logo worktree edits untouched.

## Verification

- Renderer/table comparison against `HEAD` passed for project, architecture, PDX, LSP, catalog, CLI, REST, MCP, and API catalog reference modules.
- `rtk bash scripts/test.bash tests/test_api_table.py ... -q` with the nine affected API-table contract tests: 23 passed.
- `rtk uv run python -m py_compile ...` for the shared helper, touched renderers, and helper tests.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py ...`
- `rtk bash scripts/flake.bash --ci --paths ...`
- Full test suite deferred to reduce CPU while other migration workers are active.

## Git hygiene

- Stage only the shared Markdown helper, touched API reference renderers, helper tests, and this note.
- Do not stage `node_modules/`.
