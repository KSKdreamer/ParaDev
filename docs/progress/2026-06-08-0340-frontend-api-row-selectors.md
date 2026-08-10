# Frontend API Row Selectors

Date: 2026-06-08 03:40 CST

Issues: TAL-299, TAL-295

## Summary

- Made frontend API selector metadata self-describing in the canonical SDK operation row.
- Added SDK-owned `FRONTEND_API_SELECTORS = ("operation_id", "group_id")` and exported it from `paradev.sdk`.
- Updated `surface.frontend_api` in `get_frontend_api_contract()` to list `selectors` from the SDK-owned constant.
- Updated CLI and MCP surface contract helpers to consume `FRONTEND_API_SELECTORS` instead of maintaining duplicate local selector lists.
- Updated the bilingual frontend API manual, bilingual SDK manual, bilingual developer manual, and architecture interface map.

## Tests

- Red: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations -q`
  - Failed before implementation because `surface.frontend_api` did not include `selectors`.
- Focused green: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_mcp_surface_contract_lists_sdk_owned_tools tests/test_cli.py::test_frontend_api_cli_outputs_selected_operation_and_group_json -q`
  - `4 passed`
- SDK probe:
  - Confirmed `FRONTEND_API_SELECTORS == ("operation_id", "group_id")`.
  - Confirmed `get_frontend_api_operation("surface.frontend_api")["selectors"] == ["operation_id", "group_id"]`.
- `rtk rg -n 'FRONTEND_API_SELECTORS|surface\.frontend_api.*selectors|selector vocabulary|selector 词表' src/paradev tests docs/user-manual docs/architecture/interfaces.md`
  - Confirmed source, tests, architecture docs, and user/developer manuals reference the selector boundary.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py src/paradev/sdk/__init__.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py tests/test_architecture.py`
  - `OK: 5 file(s) - no banned imports`
- `rtk bash scripts/flake.bash --ci`
  - Passed.
- `rtk bash scripts/test.bash`
  - `443 passed`
- `rtk uv build`
  - Built `dist/paradev-0.1.0.0.dev0.tar.gz` and `dist/paradev-0.1.0.0.dev0-py3-none-any.whl`.

## Review

- `FRONTEND_API_SELECTORS` is immutable at the SDK boundary, while contract payloads continue to return JSON-safe lists.
- The canonical operation row now contains the same selector names exposed by CLI, REST/OpenAPI, and MCP.
- Surface contract helpers no longer duplicate selector literals, reducing drift risk for future GUI and MCP agents.
- The slice does not add new frontend operation ids or new runtime behavior; it makes the existing selector surface discoverable from the canonical row.

## Linear

- `TAL-299`: comment `9c893a29-656f-490e-b324-34f9d44121fe`.
- `TAL-295`: comment `e24ab4b9-d65a-4e45-b4be-bb13158178d0`.
