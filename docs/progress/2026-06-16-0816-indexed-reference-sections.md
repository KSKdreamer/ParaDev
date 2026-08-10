# Indexed Reference Sections Progress

Date: 2026-06-16 08:16 CST

Linear: none

## Done

- Added shared `api_index_sections(...)` and `api_indexed_reference_sections(...)` helpers for generated API references.
- Routed CLI, REST, and MCP API reference renderers through the shared summary/index/table section helper.
- Added focused unit coverage for the new section helpers.

## Verification

- `rtk uv run black src/paradev/_api_table_markdown.py src/paradev/surfaces/rest.py src/paradev/surfaces/mcp.py src/paradev/surfaces/cli.py tests/test_api_table.py`
- `rtk bash scripts/test.bash tests/test_api_table.py -q`
- `rtk uv run python -m py_compile src/paradev/_api_table_markdown.py src/paradev/surfaces/rest.py src/paradev/surfaces/mcp.py src/paradev/surfaces/cli.py tests/test_api_table.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_rest_api_table_lists_openapi_routes tests/test_architecture.py::test_cli_api_table_lists_command_contract tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts -q`
- Generated API reference parity checked 29 catalog entries.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table_markdown.py src/paradev/surfaces/rest.py src/paradev/surfaces/mcp.py src/paradev/surfaces/cli.py tests/test_api_table.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/_api_table_markdown.py src/paradev/surfaces/rest.py src/paradev/surfaces/mcp.py src/paradev/surfaces/cli.py tests/test_api_table.py`

## Risks Or Blockers

- Full test suite was intentionally deferred to reduce CPU pressure.
- Unrelated dirty files remain in the shared worktree and were not touched.

## Next

- Consider routing project-object and API-catalog references through the same helper in a later parity-protected slice.
