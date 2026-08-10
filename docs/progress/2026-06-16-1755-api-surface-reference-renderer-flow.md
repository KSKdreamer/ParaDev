# API Surface Reference Renderer Flow Progress

Date: 2026-06-16 17:55

Linear: n/a

## Done

- Split the surface-indexed API reference renderer into explicit private helpers for table indexes, index sections, and the final field table section.
- Preserved generated Markdown order for summary, optional feature index, surface index, and API table.

## Verification

- `rtk uv run python -m py_compile src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk uv run black src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk bash scripts/test.bash tests/test_api_table.py -q`
- `rtk bash scripts/test.bash tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown tests/test_cli.py::test_project_api_cli_outputs_reference_markdown tests/test_cli.py::test_cli_api_cli_outputs_reference_markdown tests/test_cli.py::test_rest_api_cli_outputs_reference_markdown tests/test_cli.py::test_mcp_api_cli_outputs_reference_markdown -q`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_project_api_table_lists_project_object_surface tests/test_architecture.py::test_cli_api_table_lists_command_contract tests/test_architecture.py::test_rest_api_table_lists_openapi_routes tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk git diff --check -- src/paradev/_api_table_markdown.py tests/test_api_table.py`

## Risks Or Blockers

- Full-suite testing remains deferred to reduce CPU contention with the active PIHC3 migration work.
- Unrelated PIHC3, desktop, and skill-maintenance worktree changes remain untouched.

## Next

- Keep tightening API reference helper boundaries and generated table docs in small, reviewable slices.
