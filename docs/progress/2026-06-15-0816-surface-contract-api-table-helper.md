# Surface Contract API Table Helper Progress

Date: 2026-06-15 08:16 CST

Linear: none

## Done

- Migrated the surface-contract reference renderer to the shared API-table Markdown helpers.
- Migrated the CLI API reference renderer to the shared API-table Markdown helpers.
- Migrated the REST API reference renderer to the shared API-table Markdown helpers.
- Migrated the MCP API reference renderer to the shared API-table Markdown helpers.
- Preserved surface-contract summaries, command/tool/route API schemas, row ordering, manual reference output, CLI JSON output, and CLI Markdown output.

## Verification

- `rtk uv run black src/paradev/surfaces/__init__.py src/paradev/surfaces/cli.py src/paradev/surfaces/rest.py src/paradev/surfaces/mcp.py`
- `rtk uv run python -m py_compile src/paradev/surfaces/__init__.py src/paradev/surfaces/cli.py src/paradev/surfaces/rest.py src/paradev/surfaces/mcp.py`
- `rtk uv run pytest tests/test_architecture.py::test_surface_contract_catalog_lists_static_boundaries tests/test_architecture.py::test_cli_api_table_lists_command_contract tests/test_architecture.py::test_rest_api_table_lists_openapi_routes tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts tests/test_cli.py::test_architecture_cli_outputs_surface_contract_reference_markdown tests/test_cli.py::test_rest_api_cli_outputs_table_json tests/test_cli.py::test_rest_api_cli_outputs_reference_markdown tests/test_cli.py::test_mcp_api_cli_outputs_table_json tests/test_cli.py::test_mcp_api_cli_outputs_reference_markdown tests/test_cli.py::test_cli_api_cli_outputs_table_json tests/test_cli.py::test_cli_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/__init__.py src/paradev/surfaces/cli.py src/paradev/surfaces/rest.py src/paradev/surfaces/mcp.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/surfaces/__init__.py src/paradev/surfaces/cli.py src/paradev/surfaces/rest.py src/paradev/surfaces/mcp.py`
- `rtk git diff --check -- src/paradev/surfaces/__init__.py src/paradev/surfaces/cli.py src/paradev/surfaces/rest.py src/paradev/surfaces/mcp.py`

## Risks Or Blockers

- Full-suite tests were intentionally not run to avoid competing with concurrent PIHC3 migration work.
- The worktree still contains unrelated Heaven-style skill, desktop app, PIHC3, logo, loader, and `node_modules/` changes from other workers.

## Next

- Continue migrating remaining generated-reference renderers with local Markdown helper copies.
- Keep avoiding build loader, HoI4 package internals, desktop app files, and PIHC3 progress files while those slices remain active elsewhere.
