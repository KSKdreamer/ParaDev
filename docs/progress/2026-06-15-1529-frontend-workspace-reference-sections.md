# Frontend Workspace Reference Sections Progress

## Scope

- Routed Frontend API payload, workspace section, mode/status, payload coverage, surface coverage, and workspace binding summary sections through `_frontend_api_table_section()`.
- Kept all workspace-specific row renderers local so grouped operation and coverage rows remain unchanged.
- Preserved generated Frontend API reference output under the catalog-wide generated-reference parity check.

## Verification

- `rtk uv run black src/paradev/sdk/frontend_api.py`
- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk uv run python - <<'PY' ... PY`: checked 29 generated API references against disk.
- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_workspace_projection_groups_gui_actions tests/test_architecture.py::test_frontend_api_action_detail_combines_operation_form_and_workspace_context tests/test_architecture.py::test_frontend_api_workspace_actions_expose_execution_hints tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown -q`: 6 passed.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py`

Full-suite tests were deferred to keep the active loop light.
