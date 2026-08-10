# Specialized API Table Row Consolidation

## Scope

- Migrated specialized CLI, REST, MCP, SDK, catalog, and architecture API standard table renderers to the shared `table_rows()` Markdown helper.
- Kept each module's column contract local while removing repeated manual `| ... |` row assembly.
- Confirmed the generated Markdown output is unchanged for every touched renderer.

## Verification

- `rtk uv run python - <<'PY' ...` exact `HEAD` renderer comparison for CLI, REST, MCP, PDX SDK, LSP SDK, architecture, Project object, API catalog, and HB catalog references: all matched.
- `rtk bash scripts/test.bash tests/test_architecture.py::test_cli_api_table_lists_command_contract tests/test_architecture.py::test_rest_api_table_lists_openapi_routes tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts tests/test_architecture.py::test_pdx_api_table_lists_parse_format_surfaces tests/test_architecture.py::test_lsp_api_table_lists_editor_surfaces tests/test_architecture.py::test_architecture_api_table_lists_public_graph_surface tests/test_architecture.py::test_project_api_table_lists_project_object_surface tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_catalog_api_table_lists_catalog_surfaces -q`: 9 passed.
- `rtk uv run python -m py_compile src/paradev/surfaces/cli.py src/paradev/surfaces/rest.py src/paradev/surfaces/mcp.py src/paradev/sdk/pdx.py src/paradev/sdk/lsp.py src/paradev/sdk/architecture.py src/paradev/sdk/project_api.py src/paradev/surfaces/api_catalog.py src/paradev/hb/__init__.py`.
- `rtk uv run black src/paradev/surfaces/cli.py src/paradev/surfaces/rest.py src/paradev/surfaces/mcp.py src/paradev/sdk/pdx.py src/paradev/sdk/lsp.py src/paradev/sdk/architecture.py src/paradev/sdk/project_api.py src/paradev/surfaces/api_catalog.py src/paradev/hb/__init__.py`: unchanged.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/cli.py src/paradev/surfaces/rest.py src/paradev/surfaces/mcp.py src/paradev/sdk/pdx.py src/paradev/sdk/lsp.py src/paradev/sdk/architecture.py src/paradev/sdk/project_api.py src/paradev/surfaces/api_catalog.py src/paradev/hb/__init__.py`.
- `rtk bash scripts/flake.bash --paths src/paradev/surfaces/cli.py src/paradev/surfaces/rest.py src/paradev/surfaces/mcp.py src/paradev/sdk/pdx.py src/paradev/sdk/lsp.py src/paradev/sdk/architecture.py src/paradev/sdk/project_api.py src/paradev/surfaces/api_catalog.py src/paradev/hb/__init__.py`.
- `rtk git diff --check -- src/paradev/surfaces/cli.py src/paradev/surfaces/rest.py src/paradev/surfaces/mcp.py src/paradev/sdk/pdx.py src/paradev/sdk/lsp.py src/paradev/sdk/architecture.py src/paradev/sdk/project_api.py src/paradev/surfaces/api_catalog.py src/paradev/hb/__init__.py`.

## Notes

- Full-suite tests were intentionally skipped to reduce CPU contention with active PIHC3 migration work.
- `rtk gh pr status` reported no current PRs, so there were no open GitHub review threads to address in this pass.
