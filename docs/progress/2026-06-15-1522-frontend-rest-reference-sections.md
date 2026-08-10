# Frontend REST Reference Sections Progress

## Scope

- Routed the Frontend API reference REST planner/query/path/body index cluster through `_frontend_api_table_section()`.
- Kept the frontend-specific row renderers local so generated REST route and request-planner rows remain unchanged.
- Preserved the rendered `docs/user-manual/frontend-api-reference.md` output byte-for-byte under the generated-reference parity check.

## Verification

- `rtk uv run black src/paradev/sdk/frontend_api.py`
- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk uv run python - <<'PY' ... PY`: checked 29 generated API references against disk.
- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_contract_indexes_every_surface_binding_and_openapi_annotation tests/test_architecture.py::test_frontend_api_rest_request_planner_maps_values_to_query_and_body tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown -q`: 5 passed.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py`

Full-suite tests were deferred to keep the active loop light.
