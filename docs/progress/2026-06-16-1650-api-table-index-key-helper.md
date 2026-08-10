# 2026-06-16 16:50 - API table index key helper

## Scope

- Continued the generated API table refactor in `src/paradev/_api_table.py`.
- Avoided PIHC3 migration files, desktop files, and untracked `node_modules/`.
- Preserved public SDK, CLI, REST, MCP, and generated API index payload behavior.

## Changes

- Added `_api_index_keys` as the single private helper for scalar versus list-valued API index key extraction.
- Routed `api_value_indexes` through the helper.
- Kept index ordering, skip-empty handling, validation messages, and public helper signatures unchanged.

## Verification

- `rtk uv run python -m py_compile src/paradev/_api_table.py tests/test_api_table.py`
- `rtk bash scripts/test.bash tests/test_api_table.py -q`
  - `153 passed in 0.45s`
- `rtk uv run black src/paradev/_api_table.py tests/test_api_table.py`
  - `2 files left unchanged`
- `rtk bash scripts/test.bash tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown tests/test_cli.py::test_project_api_cli_outputs_reference_markdown tests/test_cli.py::test_cli_api_cli_outputs_reference_markdown tests/test_cli.py::test_rest_api_cli_outputs_reference_markdown tests/test_cli.py::test_mcp_api_cli_outputs_reference_markdown -q`
  - `5 passed in 0.63s`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_project_api_table_lists_project_object_surface tests/test_architecture.py::test_cli_api_table_lists_command_contract tests/test_architecture.py::test_rest_api_table_lists_openapi_routes tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts -q`
  - `5 passed in 0.62s`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table.py tests/test_api_table.py`
  - `OK: 2 file(s) - no banned imports`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/_api_table.py tests/test_api_table.py`
  - `2 files would be left unchanged`
- `rtk git diff --check -- src/paradev/_api_table.py tests/test_api_table.py`

## Notes

- Full-suite tests deferred to reduce CPU use.
- Existing unrelated dirty files were not staged.
