# 2026-06-15 12:09 API summary helper

## Scope

- Added a shared `api_summary_lines(table, module_label=...)` helper for generated API reference Markdown summaries.
- Reused it across the public facade/API reference renderers that emit standard summary counts.
- Kept rendered Markdown text, API table payloads, schema anchors, and indexes unchanged.
- Left unrelated desktop, skill, PIHC3, localization, and logo worktree edits untouched.

## Verification

- Renderer/table comparison against `HEAD` passed for all touched API reference modules.
- `rtk bash scripts/test.bash tests/test_api_table.py ... -q` with the affected architecture API-table tests.
- `rtk uv run python -m py_compile ...` for the shared helper, touched API modules, and `tests/test_api_table.py`.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py ...`
- `rtk bash scripts/flake.bash --ci --paths ...`
- Full test suite deferred to reduce CPU while other migration workers are active.

## Git hygiene

- Stage only the shared markdown helper, touched API reference modules, `tests/test_api_table.py`, and this note.
- Do not stage `node_modules/`.
