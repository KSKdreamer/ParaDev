# Project Find API

Date: 2026-06-08 00:10 CST

Issues: TAL-299, TAL-295

## Summary

- Implemented frontend-safe project discovery through `Project.find(path)`.
- Added CLI `project-find`, REST/OpenAPI `GET /projects/find`, MCP contract tool `project_find`, and frontend API row `project.find`.
- Returned schema `paradev.project.find.v1` with `found`, `query_path`, and either the project view or structured diagnostics.
- Kept missing or invalid manifests non-throwing for frontend preflight flows; the CLI still exits `1` when `found` is false.
- Updated English and Chinese user/developer docs to show discovery before `Project.load(...)`.

## Tests

- Red: `rtk bash scripts/test.bash tests/test_project.py::test_project_find_returns_project_view_from_nested_path tests/test_project.py::test_project_find_returns_missing_manifest_diagnostic tests/test_cli.py::test_project_find_cli_reports_found_and_missing_projects tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_mcp_surface_contract_lists_sdk_owned_tools -q`
  - Failed before implementation because `Project.find`, CLI `project-find`, REST `/projects/find`, MCP `project_find`, and the frontend API row did not exist.
- Focused green: `rtk bash scripts/test.bash tests/test_project.py::test_project_find_returns_project_view_from_nested_path tests/test_project.py::test_project_find_returns_missing_manifest_diagnostic tests/test_cli.py::test_project_find_cli_reports_found_and_missing_projects tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_mcp_surface_contract_lists_sdk_owned_tools -q`
  - `7 passed`
- Expanded focused green: `rtk bash scripts/test.bash tests/test_project.py::test_project_find_returns_project_view_from_nested_path tests/test_project.py::test_project_find_returns_missing_manifest_diagnostic tests/test_cli.py::test_project_find_cli_reports_found_and_missing_projects tests/test_architecture.py tests/test_cli.py::test_frontend_api_cli_outputs_sdk_contract_json -q`
  - `10 passed`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py src/paradev/sdk/__init__.py src/paradev/sdk/frontend_api.py src/paradev/cli.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py src/paradev/surfaces/rest.py tests/test_project.py tests/test_cli.py tests/test_architecture.py`
  - `OK: 10 file(s) - no banned imports`
- `rtk rg -n "Project.find|project-find|project_find|/projects/find|paradev.project.find.v1|project.find|project.manifest_missing" src/paradev tests docs/user-manual docs/architecture`
  - Confirmed implementation, tests, and English/Chinese docs.
- `rtk git diff --check`
  - Passed.
- `rtk bash scripts/flake.bash --ci`
  - Passed.
- `rtk bash scripts/test.bash`
  - `405 passed`
- `rtk uv build`
  - Built `dist/paradev-0.1.0.0.dev0.tar.gz` and `dist/paradev-0.1.0.0.dev0-py3-none-any.whl`.

## Review

- The operation is read-only and reuses `Project.load(...)` plus the existing project view payload.
- Missing and invalid project manifests now produce structured diagnostics that are suitable for desktop project-picker UI.
- The API remains generic project infrastructure; no PIHC3 migration, GUI implementation, project registry persistence, or module editing behavior was added.

## Linear

- `TAL-299`: comment `f2369917-76eb-4618-8116-b508d4b0db16`.
- `TAL-295`: comment `d203af4c-bf30-4bb5-b8e4-96948bbd4162`.
