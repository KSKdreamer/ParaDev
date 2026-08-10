# Module File Edit API

Date: 2026-06-08 00:41 CST

Issues: TAL-299, TAL-295

## Summary

- Implemented `Project.read_module_file(module_id, relative_path, source_root=None, encoding="utf-8")`.
- Implemented `Project.write_module_file(module_id, relative_path, text, source_root=None, create=False, encoding="utf-8")`.
- Added CLI `module-file` and `module-edit` for reading and writing one text source file inside an existing module root.
- Added REST/OpenAPI `GET /projects/modules/file` and `PATCH /projects/modules/file`.
- Added MCP contract tools `module_file` and `module_edit`.
- Added frontend API rows `module.file` and `module.edit`, both returning `paradev.module.file.v1`.
- Updated English and Chinese user/developer docs plus architecture text.

## Tests

- Red: `rtk bash scripts/test.bash tests/test_project.py::test_module_file_read_and_write_text_source tests/test_project.py::test_module_file_write_can_create_nested_text_source tests/test_project.py::test_module_file_rejects_path_escape_and_missing_write_target tests/test_cli.py::test_module_file_and_edit_cli_read_and_write_source_text tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_mcp_surface_contract_lists_sdk_owned_tools -q`
  - Failed before implementation because the SDK methods, CLI commands, REST path, frontend API rows, and MCP tools did not exist.
- First green attempt found newline drift:
  - `write_module_file` used `save_txt`, which appends a trailing newline.
  - The implementation now uses `Path.write_text(...)` intentionally so editor text is preserved exactly.
- Focused green: same red command.
  - `8 passed`
- Expanded focused green: `rtk bash scripts/test.bash tests/test_project.py::test_module_file_read_and_write_text_source tests/test_project.py::test_module_file_write_can_create_nested_text_source tests/test_project.py::test_module_file_rejects_path_escape_and_missing_write_target tests/test_cli.py::test_module_file_and_edit_cli_read_and_write_source_text tests/test_architecture.py tests/test_cli.py::test_frontend_api_cli_outputs_sdk_contract_json -q`
  - `11 passed`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py src/paradev/sdk/__init__.py src/paradev/sdk/frontend_api.py src/paradev/cli.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py src/paradev/surfaces/rest.py tests/test_project.py tests/test_cli.py tests/test_architecture.py`
  - `OK: 10 file(s) - no banned imports`
- `rtk bash scripts/flake.bash --ci`
  - Passed.
- `rtk rg -n "read_module_file|write_module_file|module-file|module-edit|module_file|module_edit|/projects/modules/file|paradev.module.file.v1|module.file|module.edit" src/paradev tests docs/user-manual docs/architecture`
  - Confirmed implementation, tests, and English/Chinese docs.
- `rtk bash scripts/test.bash`
  - `413 passed`
- `rtk uv build`
  - Built `dist/paradev-0.1.0.0.dev0.tar.gz` and `dist/paradev-0.1.0.0.dev0-py3-none-any.whl`.
- `rtk git diff --check`
  - Passed.

## Review

- The operation is text-file scoped and remains inside an existing source module root.
- Relative paths reject absolute paths, path traversal, empty segments, `.` segments, and backslashes.
- Writes reject missing files unless `create=True`; creation is limited to nested files inside the selected module.
- The payload includes module identity, source root, file-relative paths, byte size, encoding, exact text, and `written` for mutations.
- Semantic PDX editing, GUI forms, PIHC3 migration, module removal, and content-aware object renames remain out of scope.

## Linear

- `TAL-299`: comment `373beb50-b520-41bf-ac6e-1f3f1215631c`.
- `TAL-295`: comment `29aa7def-4d07-4110-8c58-378fabe7a201`.
