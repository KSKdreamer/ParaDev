# REST API Reference Progress

Date: 2026-06-15 00:50 +0800

Linear: none

## Done

- Added a generated REST/OpenAPI route table derived from `get_openapi_seed()` instead of a second hand-maintained route list.
- Added `RestApiRow`, `RestApiTable`, `REST_API_TABLE_SCHEMA`, `get_rest_api_table()`, and `render_rest_api_reference_markdown()`.
- Added CLI `paradev rest-api --json/--markdown` and registered it in the static CLI surface contract.
- Generated `docs/user-manual/rest-api-reference.md`, including method, feature, and frontend-operation reverse indexes.
- Linked the REST reference from the user manual, Python SDK page, frontend API guide, developer manual, and architecture interface contract.

## Verification

- `rtk uv run python -m py_compile src/paradev/surfaces/rest.py src/paradev/surfaces/__init__.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_rest_api_table_lists_openapi_routes tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_openapi_seed_links_rest_operations_to_frontend_api_rows tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_cli.py::test_rest_api_cli_outputs_table_json tests/test_cli.py::test_rest_api_cli_outputs_reference_markdown tests/test_cli.py::test_rest_api_cli_rejects_markdown_json_combo -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/rest.py src/paradev/surfaces/__init__.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/surfaces/rest.py src/paradev/surfaces/__init__.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_architecture.py tests/test_cli.py`
- `rtk git diff --check`

## Risks Or Blockers

- Full Python suite was intentionally not run to avoid competing with concurrent PIHC3 migration work.
- The root worktree still contains unrelated desktop, PIHC3, loader, localization, logo, and skill changes from other workers.
- Root `node_modules/` remains untracked and must not be staged.

## Next

- Continue consolidating remaining surface-specific API tables, especially MCP and project-management entry points.
- Keep route behavior changes separate from this generated-reference contract slice.
