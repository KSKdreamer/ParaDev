# CLI API REST And MCP Selector Surfaces

## Scope

- Added a direct REST selector surface for the CLI API table at `GET /cli-api`.
- Added a direct MCP selector tool contract for `cli_api`.
- Marked the CLI API reference as available through CLI, REST, MCP, frontend, and docs in the aggregate API catalog.
- Kept CLI command behavior unchanged.

## Interface Updates

- REST API table row count is now 53, with `GET /cli-api` grouped under the `cli` feature.
- MCP API table row count is now 35, with `cli_api` grouped under the `cli` feature.
- API catalog REST surface coverage is now 12 references; MCP surface coverage is now 11 references.

## Verification

- Clean staged worktree passed: `rtk uv run --extra dev --extra rest pytest -q tests/test_cli_api_rest_mcp_selectors.py tests/test_rest_api_selection.py tests/test_mcp_api_selection.py tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_rest_api_table_lists_openapi_routes tests/test_architecture.py::test_mcp_surface_contract_lists_sdk_owned_tools tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts tests/test_cli.py::test_api_catalog_cli_outputs_table_json tests/test_cli.py::test_api_catalog_cli_outputs_index_ids_json tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown tests/test_cli.py::test_rest_api_cli_outputs_table_json tests/test_cli.py::test_rest_api_cli_outputs_reference_markdown tests/test_cli.py::test_mcp_api_cli_outputs_table_json tests/test_cli.py::test_mcp_api_cli_outputs_reference_markdown` (`24 passed`).
- Clean staged worktree passed: `rtk git diff --check`.
- Clean staged worktree passed: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/rest.py src/paradev/surfaces/mcp.py src/paradev/surfaces/api_catalog.py tests/test_cli_api_rest_mcp_selectors.py`.
- Waiver: broad scan over `tests/test_architecture.py` and `tests/test_cli.py` still reports pre-existing `json` and `pathlib` imports outside this slice.
