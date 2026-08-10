# Collection Create API

Date: 2026-06-08 01:13 CST

Issues: TAL-299, TAL-295

## Summary

- Implemented `Project.create_collection(family, collection_id, source_root=None, metadata=None, write=False, force=False)`.
- Added descriptor-scoped collection creation for `src/collections/{family}/{collection_id}/meta.yaml`.
- Reused the collection authoring-plan contract so frontend callers get the same source-root, family, path, and nested diagnostics used by authoring screens.
- Added CLI `collection-create` with `--metadata KEY=VALUE`, `--write`, `--force`, and `--json`.
- Added REST/OpenAPI `POST /projects/collections`.
- Added MCP contract tool `collection_create`.
- Changed frontend API row `collection.create` from `planned` to implemented with payload `paradev.collection.create.v1`.
- Updated English and Chinese frontend API, CLI/manual, Python SDK, developer manual, and architecture docs.

## Tests

- Red: `rtk bash scripts/test.bash tests/test_project.py::test_create_collection_plans_and_writes_descriptor_metadata tests/test_project.py::test_create_collection_rejects_existing_metadata_without_force tests/test_cli.py::test_collection_create_cli_plans_and_writes_descriptor tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_mcp_surface_contract_lists_sdk_owned_tools -q`
  - Failed before implementation because `Project.create_collection`, CLI `collection-create`, REST `/projects/collections`, frontend API implementation status, CLI adapter, and MCP tool rows did not exist.
- Added descriptor-path regression coverage:
  - `test_create_collection_blocks_non_directory_descriptor_path` verifies a blocking file at the target descriptor path returns `collection_create.path_not_directory` instead of raising from `mkdir`.
- Focused green: `rtk bash scripts/test.bash tests/test_project.py::test_create_collection_plans_and_writes_descriptor_metadata tests/test_project.py::test_create_collection_rejects_existing_metadata_without_force tests/test_project.py::test_create_collection_blocks_non_directory_descriptor_path tests/test_cli.py::test_collection_create_cli_plans_and_writes_descriptor tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_mcp_surface_contract_lists_sdk_owned_tools -q`
  - `8 passed`
- Expanded focused green: `rtk bash scripts/test.bash tests/test_project.py::test_create_collection_plans_and_writes_descriptor_metadata tests/test_project.py::test_create_collection_rejects_existing_metadata_without_force tests/test_project.py::test_create_collection_blocks_non_directory_descriptor_path tests/test_cli.py::test_collection_create_cli_plans_and_writes_descriptor tests/test_architecture.py tests/test_cli.py::test_frontend_api_cli_outputs_sdk_contract_json -q`
  - `11 passed`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py src/paradev/sdk/__init__.py src/paradev/sdk/frontend_api.py src/paradev/cli.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py src/paradev/surfaces/rest.py tests/test_project.py tests/test_cli.py tests/test_architecture.py`
  - `OK: 10 file(s) - no banned imports`
- `rtk rg -n "create_collection|collection-create|collection_create|/projects/collections|paradev.collection.create.v1|collection.create|COLLECTION_CREATE_SCHEMA" src/paradev tests docs/user-manual docs/architecture`
  - Confirmed implementation, tests, and English/Chinese docs.
- `rtk bash scripts/flake.bash --ci`
  - Passed after applying the formatter-requested expression layout in `src/paradev/sdk/project.py`.
- `rtk bash scripts/test.bash`
  - `422 passed`
- `rtk uv build`
  - Built `dist/paradev-0.1.0.0.dev0.tar.gz` and `dist/paradev-0.1.0.0.dev0-py3-none-any.whl`.
- `rtk git diff --check`
  - Passed.

## Review

- The operation creates only the descriptor metadata scaffold; descriptor source files remain under `collection-edit --create`.
- Dry runs return the full payload without touching disk.
- Existing `meta.yaml` blocks writes unless `force=True`.
- Existing non-directory descriptor roots and non-directory path ancestors block writes before filesystem mutation.
- Metadata keys must be non-empty strings; values remain structured YAML values for SDK callers, while CLI `--metadata` passes string values.
- PIHC3 migration, semantic PDX transforms, collection removal, collection rename, and GUI form design remain out of scope for this slice.

## Linear

- `TAL-299`: comments `c9cfb804-aa5a-4522-9288-9c81eb07c704`, `7c840987-64d3-494c-af2d-a7a77f8b0f8b`.
- `TAL-295`: comments `385576b6-21f5-428e-a74e-673aa9238df1`, `fd0dd455-430d-466a-ae9b-b4825880f157`.
