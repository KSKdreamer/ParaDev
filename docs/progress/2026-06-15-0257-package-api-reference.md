# 2026-06-15 02:57 Package API Reference

## Done

- Added `paradev.get_package_api_table()` and `render_package_api_reference_markdown()` for the root package facade.
- Added CLI `paradev package-api` with JSON output and `--markdown` reference generation.
- Regenerated Package API, API Catalog, and CLI API references so the root facade is included in the overall API inventory.
- Linked the package facade reference from the user manual, SDK guide, architecture boundary, and developer manual.

## Verification

- `rtk uv run python -m py_compile src/paradev/package_api.py src/paradev/__init__.py src/paradev/cli.py src/paradev/surfaces/cli.py src/paradev/surfaces/api_catalog.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_package_api_table_lists_root_facade tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_cli_api_table_lists_command_contract tests/test_cli.py::test_package_api_cli_outputs_table_json tests/test_cli.py::test_package_api_cli_outputs_reference_markdown tests/test_cli.py::test_package_api_cli_rejects_markdown_json_combo tests/test_cli.py::test_api_catalog_cli_outputs_table_json tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown tests/test_cli.py::test_cli_api_cli_outputs_table_json tests/test_cli.py::test_cli_api_cli_outputs_reference_markdown -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/package_api.py src/paradev/__init__.py src/paradev/cli.py src/paradev/surfaces/cli.py src/paradev/surfaces/api_catalog.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/package_api.py src/paradev/__init__.py src/paradev/cli.py src/paradev/surfaces/cli.py src/paradev/surfaces/api_catalog.py tests/test_architecture.py tests/test_cli.py`

## Notes

- Full-suite tests were skipped to keep CPU free for parallel PIHC3 migration work.
- This slice avoids PIHC3 and desktop files; it only adds a generated table for the root Python package facade.
