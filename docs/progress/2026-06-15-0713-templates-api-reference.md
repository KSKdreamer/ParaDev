# 2026-06-15 0713 CST - Authoring Templates API Reference

## Slice

- Added the SDK authoring-template module API table in `paradev.sdk.templates`, including `TEMPLATES_API_TABLE_SCHEMA`, row/table `TypedDict`s, `get_templates_api_table()`, and `render_templates_api_reference_markdown()`.
- Registered `templates-api` in the aggregate API catalog and CLI contract, with Typer JSON/Markdown output through `paradev templates-api`.
- Generated `docs/user-manual/templates-api-reference.md` and refreshed the catalog, CLI, and surfaces generated references.
- Updated user/developer/architecture docs to point authoring-template audits at the table helper instead of copied symbol lists.

## Checks

- `rtk uv run pytest tests/test_architecture.py::test_templates_api_table_lists_authoring_template_contract tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_surfaces_api_table_lists_surface_facade tests/test_architecture.py::test_cli_api_table_lists_command_contract tests/test_cli.py::test_api_catalog_cli_outputs_table_json tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown tests/test_cli.py::test_templates_api_cli_outputs_table_json tests/test_cli.py::test_templates_api_cli_outputs_reference_markdown tests/test_cli.py::test_templates_api_cli_rejects_markdown_json_combo tests/test_cli.py::test_cli_api_cli_outputs_table_json tests/test_cli.py::test_cli_api_cli_outputs_reference_markdown tests/test_cli.py::test_surfaces_api_cli_outputs_reference_markdown`
- `rtk uv run python -m py_compile src/paradev/sdk/templates.py src/paradev/surfaces/api_catalog.py src/paradev/surfaces/cli.py src/paradev/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/templates.py src/paradev/surfaces/api_catalog.py src/paradev/surfaces/cli.py src/paradev/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/templates.py src/paradev/surfaces/api_catalog.py src/paradev/surfaces/cli.py src/paradev/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk git diff --check -- <intentional slice files>`

## Notes

- No PIHC3 migration files, desktop files, or `node_modules/` were staged for this slice.
