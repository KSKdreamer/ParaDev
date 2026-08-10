# Project Title Rename API

Date: 2026-06-07 23:58

Issues: TAL-299, TAL-295

## Summary

- Implemented title-only project rename through `Project.rename(title)`.
- Added CLI `project-rename`, REST/OpenAPI `PATCH /projects/rename`, and MCP contract tool `project_rename`.
- Updated `get_frontend_api_contract()` so `project.rename` is now `implemented` with SDK/CLI/REST/MCP pointers.
- Kept the operation intentionally scoped to `paradev.yaml` display title: it does not move the project folder, source roots, output root, build root, or `project_id`.
- Updated English and Chinese user/developer docs plus architecture text for the implemented project management surface.

## Tests

- Red: `rtk bash scripts/test.bash tests/test_project.py::test_project_rename_updates_manifest_title_without_moving_project tests/test_project.py::test_project_rename_rejects_blank_title tests/test_cli.py::test_project_rename_cli_updates_manifest_title tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_mcp_surface_contract_lists_sdk_owned_tools -q`
  - Failed before implementation because `Project.rename`, CLI `project-rename`, REST `/projects/rename`, frontend API implementation status, and MCP `project_rename` did not exist.
- Focused green: `rtk bash scripts/test.bash tests/test_project.py::test_project_rename_updates_manifest_title_without_moving_project tests/test_project.py::test_project_rename_rejects_blank_title tests/test_cli.py::test_project_rename_cli_updates_manifest_title tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_mcp_surface_contract_lists_sdk_owned_tools -q`
  - `7 passed`
- Expanded focused green: `rtk bash scripts/test.bash tests/test_project.py::test_project_rename_updates_manifest_title_without_moving_project tests/test_project.py::test_project_rename_rejects_blank_title tests/test_cli.py::test_project_rename_cli_updates_manifest_title tests/test_architecture.py tests/test_cli.py::test_frontend_api_cli_outputs_sdk_contract_json -q`
  - `10 passed`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py src/paradev/sdk/frontend_api.py src/paradev/cli.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py src/paradev/surfaces/rest.py tests/test_project.py tests/test_cli.py tests/test_architecture.py`
  - `OK: 9 file(s) - no banned imports`
- `rtk rg -n "Project.rename|project-rename|project_rename|/projects/rename|paradev.project.rename.v1|project.rename|Renamed Starter" src/paradev tests docs/user-manual docs/architecture`
  - Confirmed implementation, tests, and English/Chinese docs.
- `rtk git diff --check`
  - Passed.
- `rtk bash scripts/flake.bash --ci`
  - Passed.
- `rtk bash scripts/test.bash`
  - `402 passed`
- `rtk uv build`
  - Built `dist/paradev-0.1.0.0.dev0.tar.gz` and `dist/paradev-0.1.0.0.dev0-py3-none-any.whl`.

## Review

- The SDK mutation is deliberately narrow and reuses the existing manifest load/save path.
- The method returns a reloaded `Project`, keeping the public OOP surface simple for Python users.
- The CLI and REST wrappers return `paradev.project.rename.v1` so frontend and script consumers get the previous title plus the updated project view.
- No PIHC3 migration-specific logic, module editing, project registry, or folder moving behavior was added.

## Linear

- `TAL-299`: comment `510ba41b-fb99-4644-bd16-979b8f880ae2`.
- `TAL-295`: comment `aa963e31-31e7-40a2-926e-397d0a5b2ac9`.
