# Project Inspection Selector

Date: 2026-06-21 00:40

## Done

- Added `paradev.sdk.get_project_inspection_selection(kind=..., index_name=..., key=...)` as the shared selector helper for the project inspection contract.
- Exported the helper from `paradev.sdk` and registered it in the aggregate API catalog for `project-inspection-reference`.
- Regenerated the SDK API, project inspection, and API catalog reference pages so row counts and selector-helper indexes stay current.
- Updated architecture notes and targeted contract tests so future API catalog drift catches missing inspection selector metadata.

## Verification

- Passed `rtk uv run pytest tests/test_architecture.py::test_project_inspection_reference_lists_contract_indexes tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_cli.py::test_api_catalog_cli_outputs_table_json tests/test_api_catalog_selector_helpers.py tests/test_api_table_contracts.py::test_api_catalog_references_match_generated_manual_pages -q`.
- Passed `rtk uv run pytest tests/test_architecture.py::test_sdk_api_table_lists_facade_exports tests/test_cli.py::test_sdk_api_cli_outputs_table_json tests/test_cli.py::test_sdk_api_cli_outputs_reference_markdown -q`.
- Passed `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_references_match_generated_manual_pages tests/test_api_table_contracts.py::test_api_table_modules_expose_selection_helpers tests/test_api_table_contracts.py::test_api_catalog_rows_match_source_helper_metadata tests/test_cli_api_reference_selectors.py -q`.
- Passed `rtk uv run pytest tests/test_project.py::test_project_inspections_describes_sdk_dispatch_contract tests/test_project.py::test_project_cli_outputs_inspections_contract_json -q`.
- Passed `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py src/paradev/sdk/__init__.py src/paradev/surfaces/api_catalog.py tests/test_architecture.py tests/test_cli.py tests/test_api_catalog_selector_helpers.py`.
- Passed `rtk bash scripts/sync-readme.bash --check`.
- Passed `rtk bash scripts/flake.bash --ci`.
- Passed `rtk git diff --check`.

## Risks Or Blockers

- This is an additive SDK selector over the existing inspection contract. It does not change the behavior of `Project.inspect(...)`, REST, MCP, or CLI inspection commands.

## Next

- Keep closing catalog rows that lack shared selectors or explicit rationale, so adapters can rely on one lookup shape per maintained reference.
