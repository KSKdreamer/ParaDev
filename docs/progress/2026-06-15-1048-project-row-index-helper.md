# Project row index helper

## Scope

- Reused `append_index_entry()` for SDK project browser, project registry, and template row indexes.
- Kept row-index key types, row order, and filtered index shape unchanged.
- Left the project inspection filter index untouched because it has distinct validation semantics.

## Verification

- `rtk gh pr status`
- `rtk uv run python - <<'PY' ... PY` `_project_browser_index()`, `_project_registry_index()`, and `_template_index()` comparison with `HEAD`
- `rtk bash scripts/test.bash tests/test_project.py::test_registered_projects_accepts_explicit_and_search_root_projects tests/test_project.py::test_desktop_state_returns_active_project_view_and_registry tests/test_project.py::test_project_templates_filters_rebuild_rows_and_index tests/test_project.py::test_project_browser_returns_frontend_ready_items_without_writing -q`
- `rtk uv run python -m py_compile src/paradev/sdk/project.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/project.py`
- `rtk git diff --check -- src/paradev/sdk/project.py`

Full-suite tests were skipped to keep CPU available for PIHC3 migration workers. GitHub reported no current PRs, so there were no review threads to address directly.
