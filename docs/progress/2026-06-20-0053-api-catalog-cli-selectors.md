# API Catalog CLI Selectors

## Scope

- Added `paradev api-catalog --reference/--reference-id` as a CLI adapter for one generated API catalog row.
- Added `paradev api-catalog --index/--index-name --key` as a CLI adapter for catalog reverse-index lookups.
- Updated the CLI API contract table and generated reference docs so the new selector projections are part of the maintained public surface.

## Verification

- `rtk uv run pytest tests/test_cli.py::test_api_catalog_cli_outputs_table_json tests/test_cli.py::test_api_catalog_cli_outputs_reference_json tests/test_cli.py::test_api_catalog_cli_outputs_index_ids_json tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown tests/test_cli.py::test_api_catalog_cli_rejects_markdown_json_combo tests/test_cli.py::test_api_catalog_cli_rejects_markdown_selector_combo tests/test_cli.py::test_api_catalog_cli_rejects_ambiguous_selectors tests/test_cli.py::test_api_catalog_cli_rejects_partial_index_selector tests/test_cli.py::test_api_catalog_cli_rejects_unknown_reference tests/test_cli.py::test_cli_api_cli_outputs_table_json tests/test_cli.py::test_cli_api_cli_outputs_reference_markdown tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_cli_api_table_lists_command_contract`
- `rtk uv run pytest tests/test_cli.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_cli.py tests/test_architecture.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_cli.py tests/test_architecture.py`
- `rtk git diff --check -- src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_cli.py tests/test_architecture.py docs/user-manual/cli-api-reference.md docs/user-manual/api-catalog-reference.md`
