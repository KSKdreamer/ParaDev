# 2026-06-16 16:28 - API Markdown standard index specs

## Scope

- Continued the generated API reference-table refactor in `src/paradev/_api_table_markdown.py`.
- Avoided PIHC3 migration files, desktop files, and untracked `node_modules/`.
- Preserved public SDK, CLI, REST, MCP, and generated Markdown behavior.

## Changes

- Added `_API_STANDARD_INDEX_SECTION_SPECS` as the single private contract for the standard Module/Feature/Kind generated API index sections.
- Routed `api_standard_index_sections` through the existing generic `api_index_sections` helper.
- Removed the duplicated hard-coded `api_index_section` calls for standard reference indexes.

## Verification

- `rtk uv run python -m py_compile src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk bash scripts/test.bash tests/test_api_table.py -q`
  - `153 passed in 0.48s`
- `rtk uv run black src/paradev/_api_table_markdown.py tests/test_api_table.py`
  - `2 files left unchanged`
- `rtk bash scripts/test.bash tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown tests/test_cli.py::test_project_api_cli_outputs_reference_markdown tests/test_cli.py::test_cli_api_cli_outputs_reference_markdown tests/test_cli.py::test_rest_api_cli_outputs_reference_markdown tests/test_cli.py::test_mcp_api_cli_outputs_reference_markdown -q`
  - `5 passed in 0.73s`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_project_api_table_lists_project_object_surface tests/test_architecture.py::test_cli_api_table_lists_command_contract tests/test_architecture.py::test_rest_api_table_lists_openapi_routes tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts -q`
  - `5 passed in 0.75s`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table_markdown.py tests/test_api_table.py`
  - `OK: 2 file(s) - no banned imports`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/_api_table_markdown.py tests/test_api_table.py`
  - `2 files would be left unchanged`
- `rtk git diff --check -- src/paradev/_api_table_markdown.py tests/test_api_table.py`

## Notes

- Full-suite tests deferred to reduce CPU use.
- Existing unrelated dirty files were not staged.
