# 2026-06-15 12:34 SDK catalog index header cleanup

## Scope

- Reused `api_index_table_header(...)` in the project, PDX, LSP, architecture, and catalog API reference renderers.
- Replaced one-line local index wrapper functions with direct `index_rows(table["..._index"])` calls.
- Preserved each renderer's existing count/value labels, including Project API's `Symbols` / `Project APIs` column order.
- Kept rendered Markdown text, API table payloads, schema anchors, and indexes unchanged.
- Left unrelated desktop, skill, PIHC3, localization, and logo worktree edits untouched.

## Verification

- Renderer/table comparison against `HEAD` passed for architecture, project, PDX, LSP, and catalog API reference modules.
- `rtk bash scripts/test.bash ... -q` with the five affected architecture API-table tests.
- `rtk uv run python -m py_compile ...` for touched modules.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py ...`
- `rtk bash scripts/flake.bash --ci --paths ...`
- Full test suite deferred to reduce CPU while other migration workers are active.

## Git hygiene

- Stage only the touched API reference modules and this note.
- Do not stage `node_modules/`.
