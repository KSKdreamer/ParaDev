# Frontend Adapter Reference Sections Progress

## Scope

- Routed Frontend API SDK, MCP, CLI, LSP, binding, and group-binding summary sections through `_frontend_api_table_section()`.
- Kept adapter-specific row renderers local so binding keys, input rows, and grouped operation rows remain unchanged.
- Preserved generated Frontend API reference output under the catalog-wide generated-reference parity check.

## Verification

- `rtk uv run black src/paradev/sdk/frontend_api.py`
- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk uv run python - <<'PY' ... PY`: checked 29 generated API references against disk.
- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_surface_bindings_are_machine_readable tests/test_architecture.py::test_frontend_api_binding_index_maps_surface_calls_to_operation_ids tests/test_architecture.py::test_frontend_api_binding_lookup_helpers_return_operation_ids tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown -q`: 6 passed.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py`

Full-suite tests were deferred to keep the active loop light.
