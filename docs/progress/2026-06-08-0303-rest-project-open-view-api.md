# REST Project Open And View API

Date: 2026-06-08 03:03 CST

Issues: TAL-299, TAL-292, TAL-295

## Summary

- Added `project.open` and `project.view` REST/OpenAPI bindings as `GET /projects`.
- Updated the maintained frontend API rows to advertise SDK `Project.load`/`Project.to_view`, CLI `project`, MCP `project_open`/`project_view`, REST `GET /projects`, and payload `Project.to_view`.
- Added OpenAPI seed metadata for `GET /projects` with optional `path`, `game`, and `title`.
- Added the REST adapter route over `open_project(path, game=game, title=title).to_view()`.
- Added CLI contract metadata `project -> Project.to_view`.
- Added MCP contract metadata for `project_open` and `project_view`.
- Updated the bilingual frontend API manual, bilingual developer manual, and architecture interface map.

## Tests

- Red: `rtk bash scripts/test.bash tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_mcp_surface_contract_lists_sdk_owned_tools -q`
  - Failed before implementation because `GET /projects`, the project open/view REST fields, CLI `project` adapter metadata, and MCP `project_open`/`project_view` contracts did not exist.
- Focused green: `rtk bash scripts/test.bash tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_mcp_surface_contract_lists_sdk_owned_tools -q`
  - `4 passed`
- Contract probe:
  - Confirmed `project.open -> GET /projects`, MCP `project_open`, payload `Project.to_view`.
  - Confirmed `project.view -> GET /projects`, MCP `project_view`, payload `Project.to_view`.
  - Confirmed OpenAPI `/projects` GET parameters: `path`, `game`, `title`.
  - Confirmed demo project view returns project id `minimal_hoi4`.
  - Confirmed FastAPI runtime execution remains optional-extra gated in the default environment: `Install ParaDev with the 'rest' extra to build the local REST app.`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py src/paradev/surfaces/rest.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py tests/test_architecture.py`
  - `OK: 5 file(s) - no banned imports`
- `rtk rg -n 'project\.open|project\.view|GET /projects|project_open|project_view|Project\.to_view|Project\.load' docs/user-manual docs/architecture/interfaces.md src/paradev/sdk/frontend_api.py src/paradev/surfaces/rest.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py tests/test_architecture.py`
  - Confirmed source/docs coverage for the maintained API rows.
- `rtk bash scripts/flake.bash --ci`
  - Initially failed on a Black trailing-comma formatting diff in `src/paradev/surfaces/rest.py`; passed after adding the comma.
- `rtk bash scripts/test.bash`
  - `441 passed`
- `rtk uv build`
  - Built `dist/paradev-0.1.0.0.dev0.tar.gz` and `dist/paradev-0.1.0.0.dev0-py3-none-any.whl`.
- `rtk git diff --check`
  - Passed.

## Review

- `GET /projects` mirrors CLI `project --json`: it returns `Project.to_view` and does not introduce a new project payload schema.
- `GET /projects/find` remains the non-throwing existence/discovery check; GUI callers should use it before open when they need a missing-project diagnostic instead of an exception.
- The MCP additions are contract metadata only, matching the current MCP surface helper style.
- Runtime FastAPI route tests remain outside the default suite because the `rest` extra is optional and not installed in the default environment.

## Linear

- `TAL-299`: comment `f47a35e9-b615-4a80-920a-1367f9252ec4`.
- `TAL-292`: comment `a06cae74-f451-44ec-8c8c-e1731da2e7f9`.
- `TAL-295`: comment `891c88cc-4323-4bb3-8367-76b6347af911`.
