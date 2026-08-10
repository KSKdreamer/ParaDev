# Desktop Build Frontend API Progress

Date: 2026-06-30 14:29

Linear: TAL-000

## Done

- Added canonical frontend operation rows for `build.start`, `build.status`, and `build.interrupt`, all bound to the Python desktop facade and the `/desktop/builds` REST lifecycle routes.
- Routed native-web desktop build start/status/interrupt calls through the SDK-owned frontend API REST planner and execution helper.
- Switched the desktop build OpenAPI request schema to canonical `project_root` while preserving the legacy `projectRoot` compatibility property.
- Regenerated the frontend API TypeScript contract plus frontend, SDK/CLI, REST, and API catalog references.
- Updated architecture and frontend API prose so build lifecycle actions are documented as SDK-owned frontend operations rather than bridge-only GUI behavior.

## Verification

- `rtk uv run pytest tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_openapi_seed_links_rest_operations_to_frontend_api_rows tests/test_architecture.py::test_rest_api_table_lists_openapi_routes tests/test_architecture.py::test_frontend_api_surface_bindings_are_machine_readable tests/test_architecture.py::test_frontend_api_rest_request_planner_maps_values_to_query_and_body tests/test_architecture.py::test_frontend_api_typescript_renderer_matches_desktop_contract_file`
- `rtk uv run pytest tests/test_cli.py::test_api_catalog_cli_outputs_table_json tests/test_cli.py::test_rest_api_cli_outputs_table_json tests/test_cli.py::test_rest_api_cli_outputs_reference_markdown tests/test_cli.py::test_frontend_api_cli_outputs_sdk_contract_json tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown tests/test_cli.py::test_frontend_api_cli_plans_operation_rest_request_json tests/test_cli.py::test_frontend_api_cli_outputs_typescript_contract`
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_references_match_generated_manual_pages tests/test_api_table_contracts.py::test_api_reference_markdown_matches_renderers`
- `rtk npm --prefix apps/desktop run test:unit -- src/data/frontendApiSummary.test.ts src/data/frontendApiBindingIndex.test.ts src/services/paradev.test.ts src/data/frontendApi.test.ts`
- `rtk npm --prefix apps/desktop run build`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py src/paradev/surfaces/rest.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 47916`

## Risks Or Blockers

- Tauri still owns direct child-process handles for local desktop lifecycle control. The SDK/frontend API path is now canonical for native-web and planning, but Tauri-native execution still needs a later persistent Python owner if we want one implementation for every shell.

## Next

- Use these `build.*` lifecycle rows in the GUI build workspace so all visible build actions can be rendered, confirmed, and executed from generated action metadata.
