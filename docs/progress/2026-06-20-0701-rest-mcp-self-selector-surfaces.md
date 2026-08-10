# REST And MCP Self-Selector Surfaces

## Scope

- Added a direct REST selector surface for the REST API table at `GET /rest-api`.
- Added a direct MCP selector tool contract for `mcp_api`.
- Kept existing REST route behavior and MCP project/tool behavior unchanged.

## Interface Updates

- REST API table row count is now 52, with `GET /rest-api` grouped under the `rest` feature.
- MCP API table row count is now 34, with `mcp_api` grouped under the `mcp` feature.
- API catalog reference counts now reflect the updated REST and MCP generated references.

## Verification

- Clean staged worktree passed: `rtk uv run --extra dev --extra rest pytest -q tests/test_rest_mcp_api_self_selectors.py tests/test_rest_api_selection.py tests/test_mcp_api_selection.py tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_rest_api_table_lists_openapi_routes tests/test_architecture.py::test_mcp_surface_contract_lists_sdk_owned_tools tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts tests/test_cli.py::test_api_catalog_cli_outputs_table_json tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown tests/test_cli.py::test_rest_api_cli_outputs_table_json tests/test_cli.py::test_rest_api_cli_outputs_reference_markdown tests/test_cli.py::test_mcp_api_cli_outputs_table_json tests/test_cli.py::test_mcp_api_cli_outputs_reference_markdown` (`21 passed`).
- Clean staged worktree passed: `rtk git diff --check`.
- Clean staged worktree passed: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/rest.py src/paradev/surfaces/mcp.py tests/test_rest_mcp_api_self_selectors.py`.
- Waived: broad scan over `tests/test_architecture.py` and `tests/test_cli.py` still reports pre-existing `json` and `pathlib` imports outside this slice.
