# REST Project Create API

Date: 2026-06-08 02:51 CST

Issues: TAL-299, TAL-292, TAL-295

## Summary

- Added `project.create` to the maintained frontend-facing API as SDK `Project.create`, CLI `new`, REST/OpenAPI `POST /projects`, MCP contract `project_create`, and payload `paradev.project.create.v1`.
- Added OpenAPI seed metadata for `POST /projects` with required `path` and optional `project_id`, `title`, `game=hoi4`, and `force=false`.
- Added the REST adapter route over `create_project(...)`.
- Centralized the starter project create response in SDK helper `project_create_payload(...)`, then reused it from CLI and REST.
- Updated CLI and MCP contract helpers so project lifecycle APIs cover create/find/rename consistently.
- Updated the bilingual frontend API manual, bilingual developer manual, and architecture interface map.

## Tests

- Red: `rtk bash scripts/test.bash tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_mcp_surface_contract_lists_sdk_owned_tools -q`
  - Failed before implementation because `/projects`, the `project.create` REST/MCP fields, CLI `new` adapter metadata, and MCP `project_create` contract did not exist.
- Focused green: `rtk bash scripts/test.bash tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_mcp_surface_contract_lists_sdk_owned_tools -q`
  - `4 passed`
- Contract probe:
  - Confirmed `project.create -> POST /projects`, MCP `project_create`, and payload `paradev.project.create.v1`.
  - Confirmed OpenAPI `/projects` parameters: `path`, `project_id`, `title`, `game`, `force`.
  - Created a temporary starter project and confirmed `project_create_payload(...)` returns starter module `modifier/starter_mod_starter_modifier`.
  - Confirmed FastAPI runtime execution remains optional-extra gated in the default environment: `Install ParaDev with the 'rest' extra to build the local REST app.`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py src/paradev/sdk/__init__.py src/paradev/cli.py src/paradev/sdk/frontend_api.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py src/paradev/surfaces/rest.py tests/test_architecture.py`
  - `OK: 8 file(s) - no banned imports`
- `rtk rg -n 'project\.create|POST /projects|project_create|paradev\.project\.create\.v1|Project\.create|project_create_payload|Project.create' docs/user-manual docs/architecture/interfaces.md src/paradev/sdk/frontend_api.py src/paradev/surfaces/rest.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py tests/test_architecture.py`
  - Confirmed source/docs coverage for the maintained API row.
- `rtk bash scripts/flake.bash --ci`
  - Passed.
- `rtk bash scripts/test.bash`
  - `441 passed`
- `rtk uv build`
  - Built `dist/paradev-0.1.0.0.dev0.tar.gz` and `dist/paradev-0.1.0.0.dev0-py3-none-any.whl`.
- `rtk git diff --check`
  - Passed.

## Review

- REST remains a thin surface adapter; starter project behavior stays in `create_project(...)`.
- CLI and REST now share the same create payload helper, reducing schema drift risk for `paradev.project.create.v1`.
- The MCP change is contract metadata only, matching the current MCP surface shape in this repo.
- `force=false` remains the default in all surfaces; GUI callers should only set it after explicit user confirmation.
- Runtime FastAPI route tests remain outside the default suite because the `rest` extra is optional and not installed in the default environment.

## Linear

- `TAL-299`: comment `b683fb2a-9464-41ac-ad37-767809233e13`.
- `TAL-292`: comment `eb32b628-6c44-44ee-9b4f-1ef1b1e2cee6`.
- `TAL-295`: comment `37dd3ec3-c300-4bbe-95e9-0e6b0ae85fe4`.
