# API Row List Validation Delegation Progress

Date: 2026-06-16 15:33

Linear: N/A

## Done

- Delegated API table row-list list-like validation to the shared `_api_list_items` helper.
- Kept row mapping validation and existing error labels stable while removing duplicated guard branches.

## Verification

- `rtk bash scripts/test.bash tests/test_api_table.py -q`
- `rtk uv run python -m py_compile src/paradev/_api_table.py tests/test_api_table.py`
- `rtk uv run black src/paradev/_api_table.py tests/test_api_table.py`
- `rtk bash scripts/test.bash tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown tests/test_cli.py::test_project_api_cli_outputs_reference_markdown tests/test_cli.py::test_cli_api_cli_outputs_reference_markdown tests/test_cli.py::test_rest_api_cli_outputs_reference_markdown tests/test_cli.py::test_mcp_api_cli_outputs_reference_markdown -q`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_project_api_table_lists_project_object_surface tests/test_architecture.py::test_cli_api_table_lists_command_contract tests/test_architecture.py::test_rest_api_table_lists_openapi_routes tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table.py tests/test_api_table.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/_api_table.py tests/test_api_table.py`
- `rtk git diff --check -- src/paradev/_api_table.py tests/test_api_table.py`

## Risks Or Blockers

- Full suite deferred to reduce CPU contention while PIHC3 migration work continues.
- Unrelated dirty skill, desktop, PIHC3, loader, and local asset changes were left untouched.

## Next

- Continue simplifying shared API table helpers while keeping generated SDK, CLI, REST, and MCP reference outputs stable.
