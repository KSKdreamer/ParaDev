# Frontend API Lookup Helpers

Date: 2026-06-08 03:24 CST

Issues: TAL-299, TAL-295

## Summary

- Added SDK lookup helpers over the maintained frontend API list: `get_frontend_api_operation(operation_id)` and `get_frontend_api_group(group_id)`.
- Kept `get_frontend_api_contract()` as the single source of truth; the helpers return copied rows and group slices from the same operation table.
- Added contextual validation errors for unknown operation ids and group ids.
- Made frontend API group metadata a defensive copy in returned contracts.
- Updated the bilingual frontend API manual, bilingual SDK manual, bilingual developer manual, and architecture interface map.

## Tests

- Red: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_lookup_helpers_return_canonical_rows -q`
  - Failed before implementation because `get_frontend_api_group` and `get_frontend_api_operation` were not exported from `paradev.sdk`.
- Focused green: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_lookup_helpers_return_canonical_rows -q`
  - `1 passed`
- Focused surface green: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_frontend_api_lookup_helpers_return_canonical_rows tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_mcp_surface_contract_lists_sdk_owned_tools -q`
  - `4 passed`
- SDK probe:
  - Confirmed the contract schema `paradev.sdk.frontend-api.v1`.
  - Confirmed the contract currently lists 57 operations.
  - Confirmed `get_frontend_api_operation("module.list")["payload"] == "paradev.build.modules.v1"`.
  - Confirmed `get_frontend_api_group("modules")` returns the module operation ids from `module.list` through `module.remove`.
- `rtk rg -n "get_frontend_api_operation|get_frontend_api_group" src/paradev/sdk docs/user-manual docs/architecture/interfaces.md tests/test_architecture.py`
  - Confirmed source, tests, architecture docs, and user/developer manuals reference the helper boundary.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py src/paradev/sdk/__init__.py tests/test_architecture.py`
  - `OK: 3 file(s) - no banned imports`
- `rtk bash scripts/flake.bash --ci`
  - Passed.
- `rtk bash scripts/test.bash`
  - `442 passed`
- `rtk uv build`
  - Built `dist/paradev-0.1.0.0.dev0.tar.gz` and `dist/paradev-0.1.0.0.dev0-py3-none-any.whl`.

## Review

- The helpers do not introduce a parallel API vocabulary; they are thin validated views over `_frontend_api_operations()`.
- Unknown ids report the valid operation or group ids, which is useful for GUI/importer integration bugs.
- Returned group metadata and operation rows are copied so accidental caller mutation does not alter module-level state.
- REST, MCP, and CLI do not need new endpoints for this slice because they already expose the full contract through `frontend-api`.

## Linear

- `TAL-299`: comment `dce65575-3724-4f60-ad65-055c17eafa62`.
- `TAL-295`: comment `e5430612-d71e-40ac-ad5f-1b05335dd818`.
