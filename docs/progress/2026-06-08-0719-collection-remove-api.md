# Collection Remove API Progress

Date: 2026-06-08 07:19 CST

Linear: TAL-295, TAL-299

## Done

- Added plan-first `Project.remove_collection(...)` with payload schema `paradev.collection.remove.v1`, descriptor file inventory, `family` and `source_root` disambiguation, and explicit `write=True` deletion.
- Exposed the same operation through CLI `collection-remove`, REST/OpenAPI `DELETE /projects/collections`, MCP contract `collection_remove`, and frontend API row `collection.remove`.
- Regenerated the frontend API reference and updated the English/Chinese user manual, SDK manual, developer manual, modules/collections guide, and architecture interface docs.
- Added SDK, CLI, OpenAPI, frontend contract, reverse binding, CLI contract, and MCP contract tests.

## Verification

- `rtk uv run pytest tests/test_project.py::test_collection_remove_plans_and_removes_descriptor tests/test_cli.py::test_collection_remove_cli_plans_and_removes_descriptor tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_openapi_seed_links_rest_operations_to_frontend_api_rows tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_mcp_surface_contract_lists_sdk_owned_tools`
- `rtk uv run pytest tests/test_architecture.py::test_openapi_seed_links_rest_operations_to_frontend_api_rows tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_mcp_surface_contract_lists_sdk_owned_tools`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/cli.py src/paradev/sdk/__init__.py src/paradev/sdk/frontend_api.py src/paradev/sdk/project.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py src/paradev/surfaces/rest.py tests/test_architecture.py tests/test_cli.py tests/test_project.py`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_architecture.py`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash` (`464 passed`)
- `rtk uv run paradev frontend-api --operation collection.remove --json`
- `rtk uv run paradev frontend-api --operation collection.remove --values-json '{"path":"/workspace/mod","collection_id":"germany","family":"event","write":false}' --rest-request --json`
- `rtk git diff --check`
- `rtk uv build`

## Risks Or Blockers

- `collection.remove` deletes only discovered descriptor roots under configured source roots. Synthetic collections inferred from module metadata are not descriptor folders and remain outside this operation.
- The operation does not rewrite modules that reference the removed collection id or delete generated build artifacts; those workflows should remain separate confirmation flows.

## Next

- Continue frontend-facing parity with the next collection/module management gap, likely collection rename or source-root-aware editing refinements.
- Keep TAL-295/TAL-299 docs and generated API references synchronized with every public SDK, CLI, REST, MCP, or LSP surface change.
