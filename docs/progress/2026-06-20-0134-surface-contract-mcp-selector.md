# Surface Contract MCP Selector Progress

Date: 2026-06-20 01:34 +0800

Linear: none

## Done

- Added the read-only `surface_contracts` MCP tool contract so MCP exposes the same SDK-owned `get_surface_contract_selection(...)` selector path as REST.
- Regenerated `docs/user-manual/mcp-api-reference.md` and `docs/user-manual/api-catalog-reference.md` so the MCP table now reports 29 tools and 18 read tools.
- Updated the architecture interface guide to document the MCP selector alongside the existing SDK and REST surface-contract selector paths.
- Strengthened MCP/API catalog tests and CLI output tests to lock the selector row, feature index, and generated row counts.

## Verification

- `rtk uv run pytest -q tests/test_architecture.py::test_mcp_surface_contract_lists_sdk_owned_tools tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_cli.py::test_api_catalog_cli_outputs_table_json tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown tests/test_cli.py::test_mcp_api_cli_outputs_table_json tests/test_cli.py::test_mcp_api_cli_outputs_reference_markdown`
- `rtk uv run pytest -q tests/test_architecture.py tests/test_cli.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/mcp.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/surfaces/mcp.py tests/test_architecture.py tests/test_cli.py`

## Risks Or Blockers

- Full suite intentionally not run to keep CPU usage down while other PIHC3 migration work is active.
- The worktree still contains unrelated user/agent changes; this slice only stages the MCP selector, docs, tests, and this progress note.

## Next

- Continue reviewing selector parity across CLI, REST, MCP, and SDK API catalog surfaces before adding new surface-specific endpoints.
