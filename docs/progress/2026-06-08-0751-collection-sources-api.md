# 2026-06-08 07:51 CST - Collection Sources API

## Done

- Added `owner_kind` filtering to `Project.sources(...)` and the shared `paradev.build.sources_view(...)` helper.
- Exposed canonical frontend row `collection.sources` for descriptor-owned source inventory through SDK `Project.inspect('sources')`, CLI `sources --owner-kind collection`, REST/OpenAPI `GET /projects/inspect?kind=sources`, and MCP `project_inspect`.
- Updated the SDK-owned inspection contract so `sources` advertises the `owner_kind` filter to CLI, REST, MCP, and GUI callers.
- Regenerated `docs/user-manual/frontend-api-reference.md` and updated English/Chinese user, developer, architecture, modules/collections, SDK, and build diagnostics docs.
- Added project, CLI, OpenAPI, frontend contract, CLI contract, and MCP contract tests.

## Verification

- `rtk uv run pytest tests/test_project.py::test_project_sources_filters_collection_descriptor_owner_kind tests/test_cli.py::test_sources_cli_filters_collection_descriptor_owner_kind tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_openapi_seed_links_rest_operations_to_frontend_api_rows tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_binding_index_maps_surface_calls_to_operation_ids tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_mcp_surface_contract_lists_sdk_owned_tools`
- `rtk uv run pytest tests/test_project.py::test_project_inspections_describes_sdk_dispatch_contract tests/test_project.py::test_project_sources_filters_collection_descriptor_owner_kind tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations`
- `rtk git diff --check`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/views.py src/paradev/cli.py src/paradev/sdk/frontend_api.py src/paradev/sdk/project.py tests/test_architecture.py tests/test_cli.py tests/test_project.py`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash` (`469 passed`)
- `rtk uv build`
- `rtk uv run paradev frontend-api --operation collection.sources --json`
- `rtk uv run paradev frontend-api --operation collection.sources --values-json '{"path":"/workspace/mod","collection_id":"germany","owner_kind":"collection","loader":"loc"}' --rest-request --json`

## Review Notes

- `collection.sources` is intentionally not a new endpoint. It is the collection-descriptor projection of the existing `sources` inspection, using `owner_kind=collection` to avoid mixing descriptor-owned files with module files associated to the same collection id.
- Unsupported `owner_kind` values fail early with a contextual `ValueError`, and the CLI maps that to a parameter error.

## Next

- Continue toward generic module compilation by hardening source inventory and output views before adding broader family-specific compiler behavior.
