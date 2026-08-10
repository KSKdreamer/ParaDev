# 2026-06-08 07:33 CST - Collection Rename API

## Done

- Added `Project.rename_collection(...)` and `paradev.collection.rename.v1` for moving collection descriptor folders within the same family and source root.
- Exposed the operation across CLI `collection-rename`, REST `PATCH /projects/collections/rename`, MCP `collection_rename`, and the canonical frontend row `collection.rename`.
- Regenerated `docs/user-manual/frontend-api-reference.md` and updated English/Chinese user-manual and developer-manual pages so frontend, CLI, REST, MCP, and SDK names stay aligned.
- Added SDK, CLI, OpenAPI, frontend contract, CLI contract, and MCP contract tests for collection rename.

## Verification

- `rtk uv run pytest tests/test_project.py::test_collection_rename_moves_descriptor_without_rewriting_content tests/test_project.py::test_collection_rename_rejects_existing_destination tests/test_cli.py::test_collection_rename_cli_moves_descriptor_without_rewriting_content tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_openapi_seed_links_rest_operations_to_frontend_api_rows tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_mcp_surface_contract_lists_sdk_owned_tools`
- `rtk git diff --check`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/cli.py src/paradev/sdk/__init__.py src/paradev/sdk/frontend_api.py src/paradev/sdk/project.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py src/paradev/surfaces/rest.py tests/test_architecture.py tests/test_cli.py tests/test_project.py`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash` (`467 passed`)
- `rtk uv build`
- `rtk uv run paradev frontend-api --operation collection.rename --json`
- `rtk uv run paradev frontend-api --operation collection.rename --values-json '{"path":"/workspace/mod","collection_id":"germany","target_id":"france","family":"event"}' --rest-request --json`

## Review Notes

- Rename intentionally moves only the descriptor folder. It does not rewrite PDX identifiers, localization keys, module metadata references, or generated artifacts.
- The frontend API row, surface contracts, OpenAPI extension links, and bilingual docs now make that limitation explicit so UI confirmation copy can stay honest.

## Next

- Continue hardening frontend-facing APIs around module and collection lifecycle actions before adding broader module compilation operations.
