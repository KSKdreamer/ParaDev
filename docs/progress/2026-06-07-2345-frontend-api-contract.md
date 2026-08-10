# Frontend API Contract

Date: 2026-06-07 23:45

Issues: TAL-299, TAL-295, TAL-294

## Summary

- Added SDK-owned `get_frontend_api_contract()` with schema `paradev.sdk.frontend-api.v1`.
- Grouped frontend-facing operations across projects, modules, collections, build, PDX, LSP, catalog, and surface metadata.
- Marked implemented operations separately from `planned` gaps such as project rename, module edit, collection create, PDX format, and LSP calls.
- Exposed the same contract through CLI `frontend-api`, MCP `frontend_api`, REST/OpenAPI `GET /frontend-api`, and public Python SDK imports.
- Added bilingual manual coverage in `docs/user-manual/frontend-api.md` and linked it from SDK, developer, manual index, and architecture docs.

## Tests

- Red: `rtk bash scripts/test.bash tests/test_architecture.py tests/test_cli.py::test_frontend_api_cli_outputs_sdk_contract_json -q`
  - Failed before implementation because `/frontend-api`, `get_frontend_api_contract`, CLI `frontend-api`, and MCP `frontend_api` did not exist.
- Focused green: `rtk bash scripts/test.bash tests/test_architecture.py tests/test_cli.py::test_frontend_api_cli_outputs_sdk_contract_json -q`
  - `7 passed`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py src/paradev/sdk/__init__.py src/paradev/cli.py src/paradev/surfaces/rest.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py tests/test_architecture.py tests/test_cli.py`
  - `OK: 8 file(s) - no banned imports`
- `rtk rg -n "frontend-api|frontend_api|get_frontend_api_contract|paradev.sdk.frontend-api.v1|project.rename|module.edit|lsp.diagnostics" src/paradev docs/user-manual docs/architecture tests`
  - Confirmed implementation, tests, and English/Chinese docs.
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py src/paradev/sdk/__init__.py src/paradev/cli.py src/paradev/surfaces/rest.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py tests/test_architecture.py tests/test_cli.py`
  - Passed.
- `rtk git diff --check`
  - Passed.
- `rtk bash scripts/flake.bash --ci`
  - Passed.
- `rtk bash scripts/test.bash`
  - `399 passed`
- `rtk uv build`
  - Built `dist/paradev-0.1.0.0.dev0.tar.gz` and `dist/paradev-0.1.0.0.dev0-py3-none-any.whl`.

## Review

- The contract is additive and SDK-owned; existing CLI, SDK, REST, MCP, parser, and build behavior remains unchanged.
- Planned frontend operations are visible but not callable as stable SDK behavior, avoiding hidden UI assumptions.
- `frontend-local` currently covers active project selection, which should stay in app workspace state until there is a durable workspace API.
- The operation list embeds the existing inspection contract, so module and collection screens can reuse `Project.inspect(...)` filter metadata.

## Linear

- Created `TAL-299`: `Foundation: maintain frontend API contract`.
- `TAL-299`: comment `39eacc76-99a8-4030-9f2a-e8944d8d13c8`.
- `TAL-295`: comment `a0bfc639-0f3f-4e16-bb3d-979b2f812248`.
- `TAL-294`: comment `b758857a-87be-401d-8199-9fe21d8f26fe`.
