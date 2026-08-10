# 2026-06-15 03:16 Surfaces API Reference

## Summary

- Added a generated `paradev.surfaces` facade API table with `SURFACES_API_TABLE_SCHEMA`, typed rows, module/feature/kind indexes, and Markdown rendering.
- Exposed the table through `paradev surfaces-api`, added it to the API catalog, and regenerated the catalog, surfaces, and CLI reference docs.
- Updated focused architecture/CLI tests so future facade, catalog, or command drift is caught without running the full suite.

## Verification

- `rtk uv run python -m py_compile src/paradev/surfaces/api.py src/paradev/surfaces/__init__.py src/paradev/surfaces/api_catalog.py src/paradev/surfaces/cli.py src/paradev/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_surfaces_api_table_lists_surface_facade tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_cli_api_table_lists_command_contract tests/test_cli.py::test_surfaces_api_cli_outputs_table_json tests/test_cli.py::test_surfaces_api_cli_outputs_reference_markdown tests/test_cli.py::test_surfaces_api_cli_rejects_markdown_json_combo tests/test_cli.py::test_api_catalog_cli_outputs_table_json tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown tests/test_cli.py::test_cli_api_cli_outputs_table_json tests/test_cli.py::test_cli_api_cli_outputs_reference_markdown -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/api.py src/paradev/surfaces/__init__.py src/paradev/surfaces/api_catalog.py src/paradev/surfaces/cli.py src/paradev/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/surfaces/api.py src/paradev/surfaces/__init__.py src/paradev/surfaces/api_catalog.py src/paradev/surfaces/cli.py src/paradev/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk git diff --check -- <intentional surfaces API reference files>`
