# API Catalog REST Selector

## Scope

- Added REST/OpenAPI `GET /api-catalog` for the aggregate API catalog table.
- Added `reference_id` and `index_name`/`key` query selectors so REST clients can fetch one catalog row or one reverse-index id list.
- Marked the API catalog reference as REST-delivered and regenerated REST/API catalog reference docs.
- Synced the architecture interface note for the SDK/CLI/REST API catalog lookup surface.

## Verification

- RED: `rtk uv run pytest tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_rest_api_table_lists_openapi_routes tests/test_architecture.py::test_api_catalog_rest_route_outputs_table_reference_and_index_json tests/test_architecture.py::test_api_catalog_rest_route_rejects_invalid_selectors tests/test_cli.py::test_api_catalog_cli_outputs_table_json tests/test_cli.py::test_rest_api_cli_outputs_table_json tests/test_cli.py::test_rest_api_cli_outputs_reference_markdown`
- `rtk uv run pytest tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_rest_api_table_lists_openapi_routes tests/test_architecture.py::test_api_catalog_rest_route_outputs_table_reference_and_index_json tests/test_architecture.py::test_api_catalog_rest_route_rejects_invalid_selectors tests/test_cli.py::test_api_catalog_cli_outputs_index_ids_json tests/test_cli.py::test_api_catalog_cli_outputs_table_json tests/test_cli.py::test_rest_api_cli_outputs_table_json tests/test_cli.py::test_rest_api_cli_outputs_reference_markdown`
- `rtk uv run pytest tests/test_cli.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/rest.py src/paradev/surfaces/api_catalog.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/surfaces/rest.py src/paradev/surfaces/api_catalog.py tests/test_architecture.py tests/test_cli.py`
- `rtk git diff --check -- src/paradev/surfaces/rest.py src/paradev/surfaces/api_catalog.py tests/test_architecture.py tests/test_cli.py docs/user-manual/rest-api-reference.md docs/user-manual/api-catalog-reference.md docs/architecture/interfaces.md`
