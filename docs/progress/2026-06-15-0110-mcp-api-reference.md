# MCP API Reference Progress

Date: 2026-06-15 01:10

Linear: unassigned

## Done

- Added the generated MCP API-standard table from `paradev.surfaces.mcp.get_mcp_api_table()`.
- Added CLI `paradev mcp-api` with JSON and Markdown projections.
- Generated `docs/user-manual/mcp-api-reference.md` and linked it from the user/developer/interface docs.

## Verification

- `rtk uv run python -m py_compile src/paradev/surfaces/mcp.py src/paradev/surfaces/__init__.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts tests/test_architecture.py::test_mcp_surface_contract_lists_sdk_owned_tools tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_cli.py::test_mcp_api_cli_outputs_table_json tests/test_cli.py::test_mcp_api_cli_outputs_reference_markdown tests/test_cli.py::test_mcp_api_cli_rejects_markdown_json_combo -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/mcp.py src/paradev/surfaces/__init__.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/surfaces/mcp.py src/paradev/surfaces/__init__.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py`

## Risks Or Blockers

- Full suite intentionally not run to preserve CPU while other PIHC2-to-PIHC3 workers are active.

## Next

- Continue converting remaining static surface contracts into generated API tables without changing runtime behavior.
