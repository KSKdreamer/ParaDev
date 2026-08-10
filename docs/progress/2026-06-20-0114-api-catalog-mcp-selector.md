# API Catalog MCP Selector

## Scope

- Added `get_api_catalog_selection(...)` as the shared selector helper for full-table, single-reference, and reverse-index API catalog payloads.
- Reused that selector in CLI and REST API catalog paths while preserving the CLI's existing Typer-facing validation messages.
- Added the read-only MCP `api_catalog` contract row and marked the aggregate API catalog reference as MCP-delivered.
- Regenerated API catalog, surfaces API, and MCP API reference docs, then synced the architecture interface note.

## Verification

- RED: `rtk uv run pytest tests/test_architecture.py::test_surfaces_api_table_lists_surface_facade tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_api_catalog_helpers_reject_unknown_keys tests/test_architecture.py::test_mcp_surface_contract_lists_sdk_owned_tools tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts tests/test_cli.py::test_api_catalog_cli_outputs_table_json tests/test_cli.py::test_surfaces_api_cli_outputs_table_json tests/test_cli.py::test_mcp_api_cli_outputs_table_json tests/test_cli.py::test_mcp_api_cli_outputs_reference_markdown`
- `rtk uv run pytest tests/test_architecture.py::test_surfaces_api_table_lists_surface_facade tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_api_catalog_helpers_reject_unknown_keys tests/test_architecture.py::test_mcp_surface_contract_lists_sdk_owned_tools tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts tests/test_cli.py::test_api_catalog_cli_outputs_table_json tests/test_cli.py::test_surfaces_api_cli_outputs_table_json tests/test_cli.py::test_mcp_api_cli_outputs_table_json tests/test_cli.py::test_mcp_api_cli_outputs_reference_markdown`
- `rtk uv run pytest tests/test_architecture.py tests/test_cli.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/api_catalog.py src/paradev/surfaces/__init__.py src/paradev/surfaces/api.py src/paradev/surfaces/mcp.py src/paradev/surfaces/rest.py src/paradev/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/surfaces/api_catalog.py src/paradev/surfaces/__init__.py src/paradev/surfaces/api.py src/paradev/surfaces/mcp.py src/paradev/surfaces/rest.py src/paradev/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk git diff --check -- src/paradev/surfaces/api_catalog.py src/paradev/surfaces/__init__.py src/paradev/surfaces/api.py src/paradev/surfaces/mcp.py src/paradev/surfaces/rest.py src/paradev/cli.py tests/test_architecture.py tests/test_cli.py docs/user-manual/surfaces-api-reference.md docs/user-manual/api-catalog-reference.md docs/user-manual/mcp-api-reference.md docs/architecture/interfaces.md`
