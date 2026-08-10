# Project API Helper Indexes Progress

Date: 2026-06-15 10:06

Linear: not linked

## Done

- Reused `api_value_indexes()` for Project API helper maps that connect `Project` methods to CLI commands, frontend operation ids, and inspection kinds.
- Preserved the generated Project API table and Markdown reference output.
- Left PIHC3 migration, desktop, logo, and `node_modules/` worktree changes untouched.

## Verification

- `rtk uv run python - <<'PY' ...` comparison against `HEAD`: `get_project_api_table()` and `render_project_api_reference_markdown()` matched.
- `rtk bash scripts/test.bash tests/test_architecture.py::test_project_api_table_lists_project_object_surface tests/test_architecture.py::test_sdk_api_table_lists_facade_exports -q`
- `rtk uv run python -m py_compile src/paradev/sdk/project_api.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/project_api.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/project_api.py`
- `rtk git diff --check -- src/paradev/sdk/project_api.py`

## Risks Or Blockers

- Full-suite tests skipped to keep CPU free for PIHC3 migration workers.
- `gh pr status` reported no open PRs for this checkout, so there were no GitHub review comments to address in this pass.

## Next

- Continue consolidating API-support grouping/index helpers where outputs can be compared cheaply against `HEAD`.
