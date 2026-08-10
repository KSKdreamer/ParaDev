# API Markdown Table Field Validation

## Done

- Routed generated API Markdown table `rows`, `row_count`, and index fields through contextual table lookup helpers.
- Tightened summary counts so index fields must be mappings instead of arbitrary `len(...)`-compatible values.
- Added regression coverage for missing indexed-reference rows, missing summary fields, and scalar summary indexes.
- Kept the change outside PIHC3 migration and desktop surfaces.

## Verification

- `rtk uv run python -m py_compile src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk uv run black src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk bash scripts/test.bash tests/test_api_table.py -q`
- `rtk bash scripts/test.bash tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown tests/test_cli.py::test_project_api_cli_outputs_reference_markdown tests/test_cli.py::test_cli_api_cli_outputs_reference_markdown tests/test_cli.py::test_rest_api_cli_outputs_reference_markdown tests/test_cli.py::test_mcp_api_cli_outputs_reference_markdown -q`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_project_api_table_lists_project_object_surface tests/test_architecture.py::test_cli_api_table_lists_command_contract tests/test_architecture.py::test_rest_api_table_lists_openapi_routes tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk git diff --check -- src/paradev/_api_table_markdown.py tests/test_api_table.py`

## Risks

- Full-suite tests were intentionally deferred to keep CPU free while PIHC2 to PIHC3 migration work continues.
- Existing dirty worktree changes, including skill, desktop, and PIHC3 files, were left untouched.

## Next

- Continue tightening generated API reference contracts and diagnostics for SDK, CLI, REST, MCP, GUI, and aggregate catalog surfaces.
