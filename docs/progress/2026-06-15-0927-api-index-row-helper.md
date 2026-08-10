# API Index Row Helper

## Scope

- Added shared `index_rows()` support for generated API reference index tables.
- Migrated generated API-reference modules from repeated direct `index_row()` comprehensions to `index_rows()`.
- Kept generated Markdown output unchanged for every touched API reference renderer.

## Verification

- `rtk uv run python - <<'PY' ...` exact `HEAD` renderer comparison for 25 touched API references: all matched.
- `rtk bash scripts/test.bash tests/test_architecture.py::test_package_api_table_lists_root_facade tests/test_architecture.py::test_config_api_table_lists_public_config_facade tests/test_architecture.py::test_gui_api_table_lists_public_gui_facade tests/test_architecture.py::test_desktop_api_table_lists_public_desktop_facade tests/test_architecture.py::test_games_api_table_lists_public_games_facade tests/test_architecture.py::test_project_facade_api_table_lists_project_package_facade tests/test_architecture.py::test_localization_api_table_lists_public_localization_facade tests/test_architecture.py::test_sdk_api_table_lists_facade_exports tests/test_architecture.py::test_surfaces_api_table_lists_surface_facade tests/test_architecture.py::test_build_api_table_lists_public_build_facade tests/test_architecture.py::test_rest_facade_api_table_lists_public_api_facade tests/test_architecture.py::test_lsp_server_api_table_lists_public_lsp_facade tests/test_architecture.py::test_pdx_core_api_table_lists_public_pdx_facade tests/test_architecture.py::test_hb_api_table_lists_public_hb_facade tests/test_architecture.py::test_templates_api_table_lists_authoring_template_contract tests/test_architecture.py::test_copy_roots_api_table_lists_copy_root_contract tests/test_architecture.py::test_cli_api_table_lists_command_contract tests/test_architecture.py::test_rest_api_table_lists_openapi_routes tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts tests/test_architecture.py::test_pdx_api_table_lists_parse_format_surfaces tests/test_architecture.py::test_lsp_api_table_lists_editor_surfaces tests/test_architecture.py::test_architecture_api_table_lists_public_graph_surface tests/test_architecture.py::test_project_api_table_lists_project_object_surface tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_catalog_api_table_lists_catalog_surfaces -q`: 25 passed.
- `rtk uv run black src/paradev/_api_table_markdown.py ... src/paradev/hb/__init__.py`: unchanged for the 26 touched Python files.
- `rtk uv run python -m py_compile src/paradev/_api_table_markdown.py ... src/paradev/hb/__init__.py`.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table_markdown.py ... src/paradev/hb/__init__.py`.
- `rtk bash scripts/flake.bash --paths src/paradev/_api_table_markdown.py ... src/paradev/hb/__init__.py`.
- `rtk git diff --check -- src/paradev/_api_table_markdown.py ... src/paradev/hb/__init__.py`.

## Notes

- Full-suite tests were intentionally skipped to reduce CPU contention with active PIHC3 migration work.
- `rtk gh pr status` reported no current PRs, so there were no open GitHub review threads to address in this pass.
