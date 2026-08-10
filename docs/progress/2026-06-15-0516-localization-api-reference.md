# 2026-06-15 05:16 CST - Localization API Reference

## Scope

- Added a generated `paradev.localization` facade API table for HOI4 language alias normalization helpers.
- Registered the table in the aggregate API catalog and exposed CLI `localization-api` JSON/Markdown output.
- Regenerated the localization, API catalog, and CLI API reference pages.

## Verification

- `rtk uv run python -m py_compile src/paradev/localization/api.py src/paradev/localization/__init__.py src/paradev/surfaces/api_catalog.py src/paradev/surfaces/cli.py src/paradev/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_localization_api_table_lists_public_localization_facade tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_cli_api_table_lists_command_contract tests/test_cli.py::test_api_catalog_cli_outputs_table_json tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown tests/test_cli.py::test_localization_api_cli_outputs_table_json tests/test_cli.py::test_localization_api_cli_outputs_reference_markdown tests/test_cli.py::test_localization_api_cli_rejects_markdown_json_combo tests/test_cli.py::test_cli_api_cli_outputs_table_json tests/test_cli.py::test_cli_api_cli_outputs_reference_markdown -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/localization/api.py src/paradev/localization/__init__.py src/paradev/surfaces/api_catalog.py src/paradev/surfaces/cli.py src/paradev/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/localization/api.py src/paradev/localization/__init__.py src/paradev/surfaces/api_catalog.py src/paradev/surfaces/cli.py src/paradev/cli.py tests/test_architecture.py tests/test_cli.py`

## Non-Goals

- Did not touch PIHC3 migration code, desktop frontend work, or `node_modules/`.
