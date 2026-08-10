# 2026-06-15 02:44 API Catalog Reference

## Done

- Added `paradev.surfaces.get_api_catalog_table()` and `render_api_catalog_reference_markdown()` as the overall generated catalog for maintained API references.
- Added CLI `paradev api-catalog` with JSON output and `--markdown` reference generation.
- Regenerated the new API Catalog reference and the CLI API reference so `api-catalog` is included in command audits.
- Linked the overall catalog from the user manual, SDK guide, architecture boundary, and developer manual.
- Exposed the previously imported REST/MCP API helpers through `paradev.surfaces.__all__`.

## Verification

- `rtk uv run python -m py_compile src/paradev/surfaces/api_catalog.py src/paradev/surfaces/__init__.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_surface_contract_catalog_lists_static_boundaries tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_cli_api_table_lists_command_contract tests/test_cli.py::test_api_catalog_cli_outputs_table_json tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown tests/test_cli.py::test_api_catalog_cli_rejects_markdown_json_combo tests/test_cli.py::test_cli_api_cli_outputs_table_json tests/test_cli.py::test_cli_api_cli_outputs_reference_markdown -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/api_catalog.py src/paradev/surfaces/__init__.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/surfaces/api_catalog.py src/paradev/surfaces/__init__.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py`

## Notes

- Full-suite tests were skipped to keep CPU free for the parallel PIHC3 migration work.
- This slice avoids PIHC3 and desktop files; it only adds an overall API-reference index on top of existing SDK, CLI, REST, MCP, frontend, and surface contract tables.
