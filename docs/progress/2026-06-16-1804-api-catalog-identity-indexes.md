# API Catalog Identity Indexes Progress

Date: 2026-06-16 18:04

Linear: n/a

## Done

- Centralized API catalog source identity uniqueness checks behind `_API_CATALOG_UNIQUE_SOURCE_FIELDS`.
- Preserved duplicate `doc_page` and `markdown_cli_command` error messages while making future catalog identity constraints easier to add.

## Verification

- `rtk uv run python -m py_compile src/paradev/surfaces/api_catalog.py tests/test_architecture.py tests/test_cli.py`
- `rtk uv run black src/paradev/surfaces/api_catalog.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_api_catalog_source_index_rejects_duplicate_identity_fields tests/test_architecture.py::test_api_catalog_source_index_rejects_invalid_text_fields tests/test_architecture.py::test_api_catalog_source_index_rejects_invalid_surfaces tests/test_architecture.py::test_api_catalog_load_payload_validates_helper_metadata tests/test_cli.py::test_api_catalog_cli_outputs_table_json tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown tests/test_cli.py::test_api_catalog_cli_rejects_markdown_json_combo -q`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_project_api_table_lists_project_object_surface tests/test_architecture.py::test_cli_api_table_lists_command_contract tests/test_architecture.py::test_rest_api_table_lists_openapi_routes tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/api_catalog.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/surfaces/api_catalog.py tests/test_architecture.py tests/test_cli.py`
- `rtk git diff --check -- src/paradev/surfaces/api_catalog.py tests/test_architecture.py tests/test_cli.py`

## Risks Or Blockers

- Full-suite testing remains deferred to keep CPU available for parallel PIHC3 migration work.
- Unrelated PIHC3, desktop, and skill-maintenance worktree changes remain untouched.

## Next

- Continue tightening the API catalog and generated reference table boundaries in focused, non-overlapping slices.
