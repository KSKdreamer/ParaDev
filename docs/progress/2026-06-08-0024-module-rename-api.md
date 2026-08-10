# Module Rename API

Date: 2026-06-08 00:24 CST

Issues: TAL-299, TAL-295

## Summary

- Implemented `Project.rename_module(module_id, object_id, source_root=None)` for source-module container renames.
- Added CLI `module-rename`, REST/OpenAPI `PATCH /projects/modules/rename`, MCP contract tool `module_rename`, and frontend API row `module.rename`.
- Returned schema `paradev.module.rename.v1` with previous/current module ids, previous/current paths, `content_rewritten: false`, and the rediscovered module view.
- Kept the operation generic: it moves `modules/{family}/{object_id}` within the same family and does not rewrite PDX identifiers, localization keys, or other authored file contents.
- Updated English and Chinese user/developer docs plus architecture text.

## Tests

- Red: `rtk bash scripts/test.bash tests/test_project.py::test_module_rename_moves_source_module_without_rewriting_content tests/test_project.py::test_module_rename_rejects_existing_destination tests/test_cli.py::test_module_rename_cli_moves_source_module tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_mcp_surface_contract_lists_sdk_owned_tools -q`
  - Failed before implementation because `Project.rename_module`, CLI `module-rename`, REST `/projects/modules/rename`, frontend API implementation status, and MCP `module_rename` did not exist.
- Focused green: same command.
  - `7 passed`
- Expanded focused green: `rtk bash scripts/test.bash tests/test_project.py::test_module_rename_moves_source_module_without_rewriting_content tests/test_project.py::test_module_rename_rejects_existing_destination tests/test_project.py::test_module_rename_can_select_duplicate_module_id_source_root tests/test_cli.py::test_module_rename_cli_moves_source_module tests/test_architecture.py tests/test_cli.py::test_frontend_api_cli_outputs_sdk_contract_json -q`
  - `11 passed`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py src/paradev/sdk/__init__.py src/paradev/sdk/frontend_api.py src/paradev/cli.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py src/paradev/surfaces/rest.py tests/test_project.py tests/test_cli.py tests/test_architecture.py`
  - `OK: 10 file(s) - no banned imports`
- `rtk rg -n "rename_module|module-rename|module_rename|/projects/modules/rename|paradev.module.rename.v1|module.rename|content_rewritten" src/paradev tests docs/user-manual docs/architecture`
  - Confirmed implementation, tests, and English/Chinese docs.
- `rtk bash scripts/flake.bash --ci`
  - Passed.
- `rtk bash scripts/test.bash`
  - `409 passed`
- `rtk git diff --check`
  - Passed.
- `rtk uv build`
  - Built `dist/paradev-0.1.0.0.dev0.tar.gz` and `dist/paradev-0.1.0.0.dev0-py3-none-any.whl`.

## Review

- The mutation is constrained to the source module folder and rejects existing destinations instead of clobbering files.
- Multi-root projects can pass `source_root` to disambiguate duplicate module ids.
- The payload explicitly reports that content was not rewritten, so frontend/importer clients do not imply a semantic HoI4 object rename.
- No PIHC3 migration, GUI implementation, module file editing, module removal, or collection mutation was added.

## Linear

- `TAL-299`: comment `12fc6242-25ca-44e9-9a24-2d43fb646a91`.
- `TAL-295`: comment `d1581553-982d-4a5f-9d7e-1a70922e933e`.
