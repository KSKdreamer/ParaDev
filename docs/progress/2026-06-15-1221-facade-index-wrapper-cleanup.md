# 2026-06-15 12:21 facade index wrapper cleanup

## Scope

- Replaced redundant facade API index wrapper calls with direct `index_rows(table["..._index"])` calls.
- Removed one-line module, feature, and kind index wrapper functions from the generated facade API reference modules.
- Kept rendered Markdown text, API table payloads, schema anchors, and indexes unchanged.
- Left unrelated desktop, skill, PIHC3, localization, and logo worktree edits untouched.

## Verification

- Renderer/table comparison against `HEAD` passed for all 16 touched facade API reference modules.
- `rtk bash scripts/test.bash tests/test_api_table.py ... -q` with affected architecture API-table tests.
- `rtk uv run python -m py_compile ...` for touched API modules.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py ...`
- `rtk bash scripts/flake.bash --ci --paths ...`
- Full test suite deferred to reduce CPU while other migration workers are active.

## Git hygiene

- Stage only the touched API reference modules and this note.
- Do not stage `node_modules/`.
