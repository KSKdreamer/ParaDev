# Module Remove API

Date: 2026-06-08 01:30 CST

Issues: TAL-299, TAL-295

## Summary

- Implemented `Project.remove_module(module_id, source_root=None, write=False)`.
- Added payload schema `paradev.module.remove.v1`.
- Added CLI `module-remove` with dry-run default, `--write`, `--source-root`, and `--json`.
- Added REST/OpenAPI `DELETE /projects/modules/remove`.
- Added MCP contract tool `module_remove`.
- Changed frontend API row `module.remove` from `planned` to implemented.
- Updated English and Chinese frontend API, modules/collections, Python SDK, developer manual, and architecture docs.

## Tests

- Red: `rtk bash scripts/test.bash tests/test_project.py::test_module_remove_plans_and_removes_source_module tests/test_project.py::test_module_remove_can_select_duplicate_module_id_source_root tests/test_cli.py::test_module_remove_cli_plans_and_removes_source_module tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_mcp_surface_contract_lists_sdk_owned_tools -q`
  - Failed before implementation because `Project.remove_module`, CLI `module-remove`, REST `/projects/modules/remove`, frontend API implementation status, CLI adapter, and MCP tool rows did not exist.
- Focused green: same command.
  - `7 passed`
- Expanded focused green: `rtk bash scripts/test.bash tests/test_project.py::test_module_remove_plans_and_removes_source_module tests/test_project.py::test_module_remove_can_select_duplicate_module_id_source_root tests/test_cli.py::test_module_remove_cli_plans_and_removes_source_module tests/test_architecture.py tests/test_cli.py::test_frontend_api_cli_outputs_sdk_contract_json -q`
  - `10 passed`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py src/paradev/sdk/__init__.py src/paradev/sdk/frontend_api.py src/paradev/cli.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py src/paradev/surfaces/rest.py tests/test_project.py tests/test_cli.py tests/test_architecture.py`
  - `OK: 10 file(s) - no banned imports`
- `rtk rg -n "remove_module|module-remove|module_remove|/projects/modules/remove|paradev.module.remove.v1|module.remove|MODULE_REMOVE_SCHEMA" src/paradev tests docs/user-manual docs/architecture`
  - Confirmed implementation, tests, and English/Chinese docs.
- `rtk bash scripts/flake.bash --ci`
  - Passed.
- `rtk bash scripts/test.bash`
  - `425 passed`
- `rtk uv build`
  - Built `dist/paradev-0.1.0.0.dev0.tar.gz` and `dist/paradev-0.1.0.0.dev0-py3-none-any.whl`.
- `rtk git diff --check`
  - Passed.

## Review

- The operation is plan-first and destructive only with `write=True`.
- It reuses module discovery and `source_root` disambiguation, matching module rename and file-edit behavior.
- The payload includes project id, module id, family, source root, module root, project-relative path, diagnostics, pre-removal file inventory, and `removed`.
- Removal uses `heavenbase.utils.delete_dir` and only deletes the source module folder.
- Generated build artifacts, PDX identifiers, localization keys, collection descriptors, and semantic object references are not removed or rewritten.
- Archive/trash semantics, dependency-aware warnings, PIHC3 migration, and GUI confirmation UI remain out of scope for this slice.

## Linear

- `TAL-299`: comment `44d2fd10-3444-4efb-b911-347ae86ee322`.
- `TAL-295`: comment `5d8fcef4-f2ee-432a-857b-addf15a2f3b9`.
