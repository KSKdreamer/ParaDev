# REST operation index helper

## Scope

- Added `append_index_entry()` as a typed index append primitive for non-string API indexes.
- Reused it in `append_api_index_entry()` and the REST OpenAPI-to-frontend operation index builder.
- Kept REST/OpenAPI seed, REST API table, and generated REST reference markdown output unchanged.

## Verification

- `rtk gh pr status`
- `rtk uv run python - <<'PY' ... PY` REST seed/table/reference comparison with `HEAD`
- `rtk bash scripts/test.bash tests/test_api_table.py tests/test_architecture.py::test_openapi_seed_links_rest_operations_to_frontend_api_rows tests/test_architecture.py::test_rest_api_table_lists_openapi_routes -q`
- `rtk uv run python -m py_compile src/paradev/_api_table.py src/paradev/surfaces/rest.py tests/test_api_table.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table.py src/paradev/surfaces/rest.py tests/test_api_table.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/_api_table.py src/paradev/surfaces/rest.py tests/test_api_table.py`
- `rtk git diff --check -- src/paradev/_api_table.py src/paradev/surfaces/rest.py tests/test_api_table.py`

Full-suite tests were skipped to keep CPU available for PIHC3 migration workers. GitHub reported no current PRs, so there were no review threads to address directly.
