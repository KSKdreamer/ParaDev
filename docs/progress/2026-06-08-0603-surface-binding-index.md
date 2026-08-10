# Surface Binding Index Progress

Date: 2026-06-08 06:03

Linear: TAL-299, TAL-295

## Done

- Added `get_frontend_api_contract()["index"]["binding"]`, a SDK-derived reverse map from SDK/CLI/REST/MCP/LSP call keys back to stable frontend operation ids.
- Exposed the CLI and MCP slices as `get_cli_contract()["frontend_operation_ids"]` and `get_mcp_contract()["frontend_operation_ids"]`.
- Added `frontend-api --markdown` to the CLI projection contract so the static surface list matches the shipped CLI.
- Updated architecture and bilingual user/developer SDK manuals to describe row-level `bindings`, reverse binding lookup, and static CLI/MCP operation-id maps.

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_frontend_api_surface_bindings_are_machine_readable tests/test_architecture.py::test_frontend_api_binding_index_maps_surface_calls_to_operation_ids tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_mcp_surface_contract_lists_sdk_owned_tools -q`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py tests/test_architecture.py`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`

## Risks Or Blockers

- None in this slice. The index is generated from operation row `bindings`; future surface work must update row-level bindings instead of adding hand-maintained adapter maps.

## Next

- Continue stabilizing frontend-facing API operations that are still `planned`, with priority on module create/edit flows, PDX editor operations, and generic compilation views.
