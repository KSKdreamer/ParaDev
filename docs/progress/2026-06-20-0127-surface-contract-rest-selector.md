# Surface Contract REST Selector Progress

Date: 2026-06-20 01:27 +0800

Linear: none

## Done

- Added `paradev.surfaces.get_surface_contract_selection(...)` as the shared selector for the static surface contract summary, exact contract payloads, and status id lists.
- Added REST/OpenAPI `GET /surface-contracts` with `identifier` and `status` query selectors, sharing the SDK selector validation path.
- Regenerated `docs/user-manual/surfaces-api-reference.md`, `docs/user-manual/rest-api-reference.md`, and `docs/user-manual/api-catalog-reference.md`.
- Updated `docs/architecture/interfaces.md` so the public surface-contract interface map names the SDK selector and REST route.
- Added architecture and CLI assertions covering SDK selector behavior, route metadata, FastAPI JSON responses, invalid selectors, and generated row-count changes.

## Verification

- `rtk uv run pytest tests/test_architecture.py::test_surface_contract_catalog_lists_static_boundaries tests/test_architecture.py::test_surfaces_api_table_lists_surface_facade tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_rest_api_table_lists_openapi_routes tests/test_architecture.py::test_api_catalog_rest_route_outputs_table_reference_and_index_json tests/test_architecture.py::test_api_catalog_rest_route_rejects_invalid_selectors tests/test_architecture.py::test_surface_contracts_rest_route_outputs_summary_contract_and_status_json tests/test_architecture.py::test_surface_contracts_rest_route_rejects_invalid_selectors tests/test_cli.py::test_api_catalog_cli_outputs_table_json tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown tests/test_cli.py::test_surfaces_api_cli_outputs_table_json tests/test_cli.py::test_surfaces_api_cli_outputs_reference_markdown tests/test_cli.py::test_rest_api_cli_outputs_table_json tests/test_cli.py::test_rest_api_cli_outputs_reference_markdown`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/surfaces tests/test_architecture.py tests/test_cli.py`
- `rtk uv run pytest tests/test_architecture.py tests/test_cli.py`

## Risks Or Blockers

- Full Python test suite was intentionally not run to avoid competing with concurrent PIHC3 migration work.
- The worktree still contains unrelated desktop, loader, PIHC3, and progress-note changes from other workers.

## Next

- Continue turning REST, MCP, and CLI public lookup paths into shared SDK-owned selectors where the generated API tables show equivalent selector behavior.
- Reassess the API catalog for remaining hand-maintained route or adapter rows that can be derived from the same fixed interface contracts.
