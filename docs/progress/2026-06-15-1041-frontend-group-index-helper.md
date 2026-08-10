# Frontend group index helper

## Scope

- Reused `append_index_entry()` for frontend API operation grouping and workspace action grouping.
- Removed remaining local `setdefault(...).append(...)` grouping from `src/paradev/sdk/frontend_api.py`.
- Kept the frontend API contract, workspace projection, and generated reference markdown output unchanged.

## Verification

- `rtk gh pr status`
- `rtk uv run python - <<'PY' ... PY` frontend contract/workspace/reference comparison with `HEAD`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_frontend_api_workspace_projection_groups_gui_actions tests/test_architecture.py::test_frontend_api_binding_lookup_helpers_return_operation_ids -q`
- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py`
- `rtk git diff --check -- src/paradev/sdk/frontend_api.py`

Full-suite tests were skipped to keep CPU available for PIHC3 migration workers. GitHub reported no current PRs, so there were no review threads to address directly.
