# Frontend API Surface Selectors

Date: 2026-06-08 03:32 CST

Issues: TAL-299, TAL-295

## Summary

- Exposed SDK-owned frontend API operation and group selection through CLI, REST/OpenAPI metadata, and MCP contract metadata.
- Added CLI `frontend-api --operation/--operation-id` and `frontend-api --group/--group-id`.
- Added REST/OpenAPI `GET /frontend-api` optional `operation_id` and `group_id` query selectors.
- Added MCP `frontend_api` selector metadata with `operation_id` and `group_id`.
- Converted unknown CLI selector ids from tracebacks into normal Typer parameter errors.
- Updated the bilingual frontend API manual, bilingual developer manual, and architecture interface map.

## Tests

- Red: `rtk bash scripts/test.bash tests/test_cli.py::test_frontend_api_cli_outputs_selected_operation_and_group_json -q`
  - Failed before implementation because `frontend-api` did not accept `--operation`.
- Red: `rtk bash scripts/test.bash tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_mcp_surface_contract_lists_sdk_owned_tools -q`
  - Failed before implementation because OpenAPI, CLI contract, and MCP contract metadata did not advertise frontend API selectors.
- Red: focused CLI selector test failed after the first implementation because unknown operation ids still surfaced as raw `ValueError` results.
- Focused green: `rtk bash scripts/test.bash tests/test_cli.py::test_frontend_api_cli_outputs_sdk_contract_json tests/test_cli.py::test_frontend_api_cli_outputs_selected_operation_and_group_json tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_mcp_surface_contract_lists_sdk_owned_tools -q`
  - `5 passed`
- Final focused green: `rtk bash scripts/test.bash tests/test_cli.py::test_frontend_api_cli_outputs_selected_operation_and_group_json tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_mcp_surface_contract_lists_sdk_owned_tools -q`
  - `4 passed`
- CLI probes:
  - `rtk uv run paradev frontend-api --operation module.list --json` returned the `module.list` operation row.
  - `rtk uv run paradev frontend-api --group modules --json` returned the `modules` group slice.
  - `rtk uv run paradev frontend-api --operation nope --json` returned a normal command error without a traceback.
- Metadata probe:
  - Confirmed OpenAPI `/frontend-api` parameter names: `operation_id`, `group_id`.
  - Confirmed CLI contract `filters["frontend-api"] == ["operation_id", "group_id"]`.
  - Confirmed MCP `frontend_api` selectors: `operation_id`, `group_id`.
- `rtk rg -n -- "--operation|--group|operation_id|group_id|frontend-api.*selector|frontend_api.*selector" src/paradev docs/user-manual docs/architecture/interfaces.md tests`
  - Confirmed source, tests, architecture docs, and user/developer manuals reference the selector boundary.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/cli.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py src/paradev/surfaces/rest.py tests/test_cli.py tests/test_architecture.py`
  - `OK: 6 file(s) - no banned imports`
- `rtk bash scripts/flake.bash --ci`
  - Passed.
- `rtk bash scripts/test.bash`
  - `443 passed`
- `rtk uv build`
  - Built `dist/paradev-0.1.0.0.dev0.tar.gz` and `dist/paradev-0.1.0.0.dev0-py3-none-any.whl`.

## Review

- The selector names mirror the SDK lookup helper arguments and do not add new frontend operation ids.
- CLI, REST/OpenAPI, and MCP now expose the same `operation_id`/`group_id` selector vocabulary.
- The REST runtime returns HTTP 400 for selector conflicts or unknown ids instead of surfacing generic server failures.
- The full contract remains the default response for `frontend-api`, `frontend_api`, and `GET /frontend-api`.

## Linear

- `TAL-299`: comment `844bc995-67e2-49c4-96bc-92bfcdb1a482`.
- `TAL-295`: comment `1d0700fb-5e8a-41b4-a19b-dc0f74a917d3`.
