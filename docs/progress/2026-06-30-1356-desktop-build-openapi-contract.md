# Desktop Build OpenAPI Contract Progress

Date: 2026-06-30 13:56

Linear: TAL-000

## Done

- Added OpenAPI seed rows for the native-web desktop build lifecycle routes: `POST /desktop/builds`, `GET /desktop/builds/status`, and `POST /desktop/builds/interrupt`.
- Made the REST API table and CLI reference expose those runtime routes under the desktop feature.
- Regenerated the REST API reference and aggregate API catalog reference.
- Updated the developer manual route inventory so the desktop build lifecycle is not documented as an ad hoc bridge-only path.

## Verification

- `rtk uv run pytest tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_rest_api_table_lists_openapi_routes tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_cli.py::test_api_catalog_cli_outputs_table_json tests/test_cli.py::test_rest_api_cli_outputs_table_json tests/test_cli.py::test_rest_api_cli_outputs_reference_markdown tests/test_cli_api_rest_mcp_selectors.py::test_cli_api_openapi_and_rest_api_row_advertise_selector tests/test_rest_mcp_api_self_selectors.py::test_generated_references_document_rest_and_mcp_self_selectors tests/test_rest_api_selection.py::test_rest_api_reference_documents_selection_helper tests/test_api_table_contracts.py::test_api_catalog_references_match_generated_manual_pages tests/test_api_table_contracts.py::test_api_reference_markdown_matches_renderers`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/rest.py tests/test_architecture.py tests/test_cli.py tests/test_cli_api_rest_mcp_selectors.py tests/test_rest_mcp_api_self_selectors.py`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 47914`

## Risks Or Blockers

- These routes remain native desktop lifecycle routes, not canonical frontend API operations. Adding generated frontend operation ids for build start/status/interrupt should be a separate product decision because the current GUI uses direct Tauri/native-web service calls.

## Next

- Continue reducing bridge-only behavior by either adding explicit frontend operation rows for desktop lifecycle actions or moving the Tauri lifecycle to a persistent Python owner.
