# 2026-06-15 12:28 facade standard row helper

## Scope

- Added shared `api_symbol_table_rows(...)` and `api_symbol_markdown_value_table_rows(...)` helpers for generated API standard-table rows.
- Reused the helpers across facade API reference renderers and removed one-line local standard-table wrapper functions.
- Kept rendered Markdown text, API table payloads, schema anchors, and indexes unchanged.
- Left unrelated desktop, skill, PIHC3, localization, and logo worktree edits untouched.

## Verification

- Renderer/table comparison against `HEAD` passed for all 16 touched facade API reference modules.
- `rtk bash scripts/test.bash tests/test_api_table.py ... -q` with affected architecture API-table tests.
- `rtk uv run python -m py_compile ...` for the shared helper, touched API modules, and `tests/test_api_table.py`.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py ...`
- `rtk bash scripts/flake.bash --ci --paths ...`
- Full test suite deferred to reduce CPU while other migration workers are active.

## Git hygiene

- Stage only the shared markdown helper, touched API reference modules, `tests/test_api_table.py`, and this note.
- Do not stage `node_modules/`.
