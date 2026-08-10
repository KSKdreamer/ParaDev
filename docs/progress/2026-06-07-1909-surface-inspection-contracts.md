# 2026-06-07 19:09 Surface Inspection Contracts

## Scope

- Continued foundation work on `codex/scaffold-source-root-selection`.
- Focused on keeping CLI, MCP, REST, and OpenAPI surfaces aligned with the SDK-owned inspection and PDX parse contracts.
- Added adapter-facing contract metadata without adding GUI, PIHC3 migration, or surface-owned domain logic.

## Changes

- Expanded `get_cli_contract()` with current read-only build inspection commands, `parse`, and command-to-SDK adapter hints.
- Expanded `get_mcp_contract()` with read-only tool contracts for `project_inspections`, `project_inspect`, and `pdx_parse`, while preserving the older architecture/project tool names.
- Expanded `get_openapi_seed()` with `/pdx/parse`, `/projects/inspections`, and `/projects/inspect` paths.
- Added matching optional FastAPI route functions in `build_app()` that delegate to `parse_pdx_file(...)`, `Project.inspect("inspections")`, and `Project.inspect(kind, **filters)`.
- Updated the developer manual and architecture surface-boundary docs to direct adapter agents to the contract helpers.

## Verification

- Red tests first:
  - `rtk uv run pytest tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_mcp_surface_contract_lists_sdk_owned_tools` failed with missing OpenAPI paths, missing CLI command entries, and missing MCP `tool_contracts`.
- Focused green:
  - `rtk uv run pytest tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_mcp_surface_contract_lists_sdk_owned_tools`.
  - `rtk uv run pytest tests/test_architecture.py` (`5 passed`).
- Surface smoke:
  - `rtk uv run python` importing `get_cli_contract`, `get_mcp_contract`, and `get_openapi_seed`, JSON-encoding all three, and checking the new inspection/parse entries.
- Format:
  - `rtk uv run black src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py src/paradev/surfaces/rest.py tests/test_architecture.py`.
- Heaven-style scan:
  - `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py src/paradev/surfaces/rest.py tests/test_architecture.py`.
- Whitespace review:
  - `rtk git diff --check`.
- Lint gate:
  - `rtk bash scripts/flake.bash --ci`.
- Test gate:
  - `rtk bash scripts/test.bash` (`359 passed`).
- Build gate:
  - `rtk uv build`.

## Review

- Surface contracts now advertise the SDK inspection and parser capabilities that GUI/MCP/REST agents need.
- REST and MCP remain read-only adapter contracts; no domain logic moved out of the SDK.
- FastAPI is optional in this environment, so runtime route behavior was kept import-safe and verified through the OpenAPI seed plus package build.
- No PIHC3 migration or GUI files were touched.

## Linear

- Attempted to read `TAL-295`; Linear MCP returned `UNAUTHORIZED` / `Session expired`.
- Attempted to read `TAL-293`; Linear MCP returned the same auth error.
- Linear updates could not be posted from this session until the app is re-authenticated.
