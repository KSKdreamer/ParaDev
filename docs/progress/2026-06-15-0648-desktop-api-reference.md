# Desktop API Reference

## Scope

- Added the public `paradev.desktop` facade around the SDK-owned desktop state contract.
- Added generated `desktop-api` JSON/Markdown reference output and catalog/CLI registration.
- Refreshed the API catalog, CLI API, and surfaces API reference pages to include `desktop-api`.
- Left the React/Tauri desktop app, PIHC3 migration files, skill files, and `node_modules/` untouched.

## Verification

- `rtk uv run python -m py_compile src/paradev/desktop/__init__.py src/paradev/desktop/api.py src/paradev/surfaces/api_catalog.py src/paradev/surfaces/cli.py src/paradev/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk uv run pytest tests/test_architecture.py::test_desktop_api_table_lists_public_desktop_facade tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_surfaces_api_table_lists_surface_facade tests/test_architecture.py::test_cli_api_table_lists_command_contract tests/test_cli.py::test_api_catalog_cli_outputs_table_json tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown tests/test_cli.py::test_desktop_api_cli_outputs_table_json tests/test_cli.py::test_desktop_api_cli_outputs_reference_markdown tests/test_cli.py::test_desktop_api_cli_rejects_markdown_json_combo tests/test_cli.py::test_cli_api_cli_outputs_table_json tests/test_cli.py::test_cli_api_cli_outputs_reference_markdown tests/test_cli.py::test_surfaces_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/desktop/__init__.py src/paradev/desktop/api.py src/paradev/surfaces/api_catalog.py src/paradev/surfaces/cli.py src/paradev/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/desktop/__init__.py src/paradev/desktop/api.py src/paradev/surfaces/api_catalog.py src/paradev/surfaces/cli.py src/paradev/cli.py tests/test_architecture.py tests/test_cli.py`
