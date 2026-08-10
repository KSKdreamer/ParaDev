# API Markdown Value Row Helper

## Scope

- Added a shared `api_symbol_markdown_value_table_row()` helper for API standard tables whose `value` column is rendered as plain Markdown.
- Migrated the games, desktop, templates, and copy-roots API reference renderers away from duplicated 12-column row builders.
- Preserved the existing generated Markdown output for all touched renderers.

## Verification

- `rtk uv run python - <<'PY' ...` exact `HEAD` renderer comparison for games, desktop, templates, and copy roots: all matched.
- `rtk bash scripts/test.bash tests/test_architecture.py::test_games_api_table_lists_public_games_facade tests/test_architecture.py::test_desktop_api_table_lists_public_desktop_facade tests/test_architecture.py::test_templates_api_table_lists_authoring_template_contract tests/test_architecture.py::test_copy_roots_api_table_lists_copy_root_contract -q`: 4 passed.
- `rtk uv run python -m py_compile src/paradev/_api_table_markdown.py src/paradev/games/api.py src/paradev/desktop/api.py src/paradev/sdk/templates.py src/paradev/sdk/copy_roots.py`.
- `rtk uv run black src/paradev/_api_table_markdown.py src/paradev/games/api.py src/paradev/desktop/api.py src/paradev/sdk/templates.py src/paradev/sdk/copy_roots.py`: unchanged.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table_markdown.py src/paradev/games/api.py src/paradev/desktop/api.py src/paradev/sdk/templates.py src/paradev/sdk/copy_roots.py`.
- `rtk bash scripts/flake.bash --paths src/paradev/_api_table_markdown.py src/paradev/games/api.py src/paradev/desktop/api.py src/paradev/sdk/templates.py src/paradev/sdk/copy_roots.py`.
- `rtk git diff --check -- src/paradev/_api_table_markdown.py src/paradev/games/api.py src/paradev/desktop/api.py src/paradev/sdk/templates.py src/paradev/sdk/copy_roots.py`.

## Notes

- Full-suite tests were intentionally skipped to reduce CPU contention with active PIHC3 migration work.
- `rtk gh pr status` reported no current PRs, so there were no open GitHub review threads to address in this pass.
