# Static Inspection Contract

Date: 2026-06-07 23:20

Issues: TAL-294, TAL-295

## Summary

- Added public `get_project_inspection_contract()` so adapters can discover `Project.inspect(...)` kinds, SDK methods, CLI command names, filters, and indexes before loading a project.
- Kept `Project.inspections()` payload-compatible by delegating to the same helper and adding the loaded `project_id`.
- Exposed the SDK-owned inspection contract in static surface metadata: `get_cli_contract()["inspection_contract"]`, MCP `project_inspect.inspection_contract`, and OpenAPI `/projects/inspect` `x-paradev-inspection-contract`.
- Updated English and Chinese manuals plus architecture/build-flow docs so GUI, MCP, REST, CLI, and importer agents can reuse one inspection metadata contract.

## Tests

- Red: `rtk bash scripts/test.bash tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_mcp_surface_contract_lists_sdk_owned_tools tests/test_project.py::test_project_inspections_describes_sdk_dispatch_contract -q`
  - Failed before implementation because the public SDK helper, CLI metadata, MCP metadata, and OpenAPI vendor extension were absent.
- Focused green: `rtk bash scripts/test.bash tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_mcp_surface_contract_lists_sdk_owned_tools tests/test_project.py::test_project_inspections_describes_sdk_dispatch_contract -q`
  - `4 passed`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py src/paradev/sdk/__init__.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py src/paradev/surfaces/rest.py tests/test_architecture.py tests/test_project.py`
  - `OK: 7 file(s) - no banned imports`
- `rtk rg -n 'get_project_inspection_contract|inspection_contract|x-paradev-inspection-contract|Project\.inspections|Project\.inspect' src/paradev docs/user-manual docs/architecture/interfaces.md docs/workflows/build-flow.md tests/test_architecture.py tests/test_project.py`
  - Confirmed SDK, CLI, MCP, REST/OpenAPI, manuals, architecture, workflow, and tests reference the static inspection contract.
- `rtk git diff --check`
  - Passed.
- `rtk bash scripts/flake.bash --ci`
  - Passed.
- `rtk bash scripts/test.bash`
  - `397 passed`
- `rtk uv build`
  - Built `dist/paradev-0.1.0.0.dev0.tar.gz` and `dist/paradev-0.1.0.0.dev0-py3-none-any.whl`.

## Review

- The change is additive. Existing project-bound `Project.inspections()` callers keep the same schema, rows, index, and `project_id`.
- Static surfaces now carry SDK-owned filter metadata without reading Typer/FastAPI implementation details or loading a demo project.
- No PIHC3 migration or GUI implementation code was added.

## Linear

- `TAL-295` updated with comment `f01d1476-62ae-4bc2-a497-4ba719b42663`.
- `TAL-294` updated with comment `49741c87-97fe-481c-888e-ecb07e40ee10`.
