# Frontend binding index helper

## Scope

- Added `append_api_nested_index_entry()` for nested API reference index buckets.
- Reused the helper in the frontend API binding index builder.
- Kept the frontend API contract and generated reference markdown output unchanged.

## Verification

- `rtk gh pr status`
- `rtk uv run python - <<'PY' ... PY` frontend contract/reference comparison with `HEAD`
- `rtk bash scripts/test.bash tests/test_api_table.py tests/test_architecture.py::test_frontend_api_binding_index_maps_surface_calls_to_operation_ids tests/test_architecture.py::test_frontend_api_binding_lookup_helpers_return_operation_ids -q`
- `rtk uv run python -m py_compile src/paradev/_api_table.py src/paradev/sdk/frontend_api.py tests/test_api_table.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table.py src/paradev/sdk/frontend_api.py tests/test_api_table.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/_api_table.py src/paradev/sdk/frontend_api.py tests/test_api_table.py`
- `rtk git diff --check -- src/paradev/_api_table.py src/paradev/sdk/frontend_api.py tests/test_api_table.py`

Full-suite tests were skipped to keep CPU available for PIHC3 migration workers. GitHub reported no current PRs, so there were no review threads to address directly.
