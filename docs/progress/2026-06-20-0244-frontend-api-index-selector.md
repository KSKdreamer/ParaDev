# 2026-06-20 02:44 +0800 - Frontend API index selector

## Scope

- Added a flat frontend API index lookup path to `get_frontend_api_selection(index_name=..., key=...)` for group, status, mode, surface, payload, and workspace section indexes.
- Exposed the same selector through `paradev frontend-api --index ... --key ...`, REST `GET /frontend-api?index_name=...&key=...`, and the MCP `frontend_api` tool metadata.
- Regenerated the SDK, CLI, REST, MCP, frontend API, and catalog reference tables so the public API matrix stays aligned.

## Verification

- Red check before implementation: targeted architecture/CLI tests failed on missing selector args and table rows.
- Focused green check after implementation: `rtk uv run pytest -q tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_rest_api_table_lists_openapi_routes tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_cli_api_table_lists_command_contract tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts tests/test_cli.py::test_api_catalog_cli_outputs_table_json tests/test_cli.py::test_frontend_api_cli_outputs_index_lookup_json tests/test_cli.py::test_cli_api_cli_outputs_table_json tests/test_cli.py::test_cli_api_cli_outputs_reference_markdown tests/test_cli.py::test_rest_api_cli_outputs_table_json tests/test_cli.py::test_rest_api_cli_outputs_reference_markdown tests/test_cli.py::test_mcp_api_cli_outputs_table_json tests/test_cli.py::test_mcp_api_cli_outputs_reference_markdown` -> 14 passed.
- Affected module check: `rtk uv run pytest -q tests/test_architecture.py tests/test_cli.py tests/test_api_table.py` -> 376 passed.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py src/paradev/cli.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py src/paradev/surfaces/rest.py tests/test_architecture.py tests/test_cli.py` -> OK.
- Focused flake check: `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py src/paradev/cli.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py src/paradev/surfaces/rest.py tests/test_architecture.py tests/test_cli.py` -> unchanged.
- Full suite skipped to preserve CPU while PIHC3 migration work is active; this slice only touches selector routing and generated API-reference rows.

## Big picture

- This keeps frontend operation-id indexes behind one SDK selector and one documented CLI/REST/MCP projection instead of requiring GUI or tool clients to depend on ad hoc helper names.
- Binding lookup remains a separate two-dimensional selector because it is keyed by binding surface plus binding key, not a flat API-table index.
