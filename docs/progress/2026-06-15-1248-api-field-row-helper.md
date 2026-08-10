# 2026-06-15 12:48 API field row helper

## Scope

- Added `api_field_table_rows(...)` for generated API standard tables that render selected mapping fields.
- Routed project, architecture, PDX, LSP, catalog, CLI, REST, MCP, and API catalog standard-table row renderers through the shared helper.
- Preserved each renderer's local field order, list-valued columns, and plain Markdown columns.
- Kept rendered Markdown text and API table payloads unchanged.
- Left unrelated desktop, skill, PIHC3, localization, and logo worktree edits untouched.

## Verification

- Renderer/table comparison against `HEAD` passed for project, architecture, PDX, LSP, catalog, CLI, REST, MCP, and API catalog reference modules.
- `rtk bash scripts/test.bash tests/test_api_table.py ... -q` with the nine affected API-table contract tests: 21 passed.
- `rtk uv run python -m py_compile ...` for the shared helper, touched renderers, and helper tests.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py ...`
- `rtk bash scripts/flake.bash --ci --paths ...`
- Full test suite deferred to reduce CPU while other migration workers are active.

## Git hygiene

- Stage only the shared Markdown helper, touched API reference renderers, helper tests, and this note.
- Do not stage `node_modules/`.
