# 2026-06-15 13:01 API symbol field renderer

## Scope

- Routed package-style API symbol table headers and rows through the shared field-list Markdown renderer.
- Kept `api_symbol_table_row(...)`, `api_symbol_table_rows(...)`, `api_symbol_markdown_value_table_row(...)`, and `api_symbol_markdown_value_table_rows(...)` as the existing helper front doors.
- Added `_API_SYMBOL_FIELDS` so the symbol table header and row rendering share one field order.
- Removed the bespoke `_api_symbol_table_row(...)` cell-by-cell renderer and the now-unused `Callable` import.
- Kept rendered Markdown text and API table payloads unchanged for all affected facade renderers.
- Left unrelated desktop, skill, PIHC3, localization, and logo worktree edits untouched.

## Verification

- Renderer/table comparison against `HEAD` passed for 16 facade API reference modules that use `api_symbol_table_rows(...)` or `api_symbol_markdown_value_table_rows(...)`.
- `rtk bash scripts/test.bash tests/test_api_table.py -q`: 14 passed.
- `rtk uv run python -m py_compile src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/_api_table_markdown.py tests/test_api_table.py`
- Full test suite deferred to reduce CPU while other migration workers are active.

## Git hygiene

- Stage only the shared Markdown helper, helper tests, and this note.
- Do not stage `node_modules/`.
