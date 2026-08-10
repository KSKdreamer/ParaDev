# Inspection CLI Selectors Progress

Date: 2026-06-21 00:49

Linear: N/A

## Done

- Added stable selector forms for `paradev inspections`: `--kind` and `--index --key`.
- Registered the new inspection selector paths in the CLI surface contract so generated API tables expose the SDK adapter.
- Regenerated the CLI API reference and API catalog reference after the row count moved to 195.
- Left the parallel desktop focus-tree layout work untouched.

## Verification

- `rtk uv run pytest tests/test_cli.py::test_inspections_cli_outputs_reference_markdown tests/test_cli.py::test_inspections_cli_outputs_kind_selector_json tests/test_cli.py::test_inspections_cli_outputs_filter_index_selector_json tests/test_cli.py::test_inspections_cli_rejects_markdown_json_combo tests/test_cli.py::test_inspections_cli_rejects_selector_conflicts tests/test_cli_api_reference_selectors.py -q`
- `rtk uv run pytest tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_cli_api_table_lists_command_contract tests/test_cli.py::test_cli_api_cli_outputs_table_json tests/test_cli.py::test_cli_api_cli_outputs_reference_markdown tests/test_cli.py::test_api_catalog_cli_outputs_table_json tests/test_api_table_contracts.py::test_api_catalog_references_match_generated_manual_pages -q`
- `rtk uv run pytest tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_cli.py::test_api_catalog_cli_outputs_table_json tests/test_cli.py::test_inspections_cli_outputs_kind_selector_json tests/test_cli.py::test_inspections_cli_outputs_filter_index_selector_json tests/test_cli.py::test_inspections_cli_rejects_selector_conflicts tests/test_cli_api_reference_selectors.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_cli.py tests/test_cli_api_reference_selectors.py tests/test_architecture.py`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/sync-readme.bash --check`
- `rtk git diff --check -- src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_cli.py tests/test_cli_api_reference_selectors.py tests/test_architecture.py docs/user-manual/cli-api-reference.md docs/user-manual/api-catalog-reference.md docs/progress/README.md docs/progress/2026-06-21-0049-inspection-cli-selectors.md`

## Risks Or Blockers

- This is an additive static selector path; existing project-bound `paradev inspections <path>` behavior is unchanged.
- The focus-tree editor is still evolving in separate desktop files and was not included in this checkpoint.

## Next

- Keep CLI, REST, MCP, and generated catalog selector metadata aligned as new project inspection references are promoted.
