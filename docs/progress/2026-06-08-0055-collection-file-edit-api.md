# Collection File Edit API

Date: 2026-06-08 00:55 CST

Issues: TAL-299, TAL-295

## Summary

- Implemented `Project.read_collection_file(collection_id, relative_path, family=None, source_root=None, encoding="utf-8")`.
- Implemented `Project.write_collection_file(collection_id, relative_path, text, family=None, source_root=None, create=False, encoding="utf-8")`.
- Added CLI `collection-file` and `collection-edit` for reading and writing one text file inside an existing collection descriptor root.
- Added REST/OpenAPI `GET /projects/collections/file` and `PATCH /projects/collections/file`.
- Added MCP contract tools `collection_file` and `collection_edit`.
- Added frontend API row `collection.file` and changed `collection.edit` from `planned` to implemented, both returning `paradev.collection.file.v1`.
- Updated English and Chinese user/developer docs plus architecture text.

## Tests

- Red: `rtk bash scripts/test.bash tests/test_project.py::test_collection_file_read_and_write_text_source tests/test_project.py::test_collection_file_write_can_create_nested_text_source tests/test_project.py::test_collection_file_rejects_path_escape_and_missing_write_target tests/test_cli.py::test_collection_file_and_edit_cli_read_and_write_descriptor_text tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_mcp_surface_contract_lists_sdk_owned_tools -q`
  - Failed before implementation because the SDK methods, CLI commands, REST path, frontend API rows, and MCP tools did not exist.
- First implementation rerun found three issues:
  - Collection roots needed source-root detection under `source_root/collections` rather than the module-only `source_root/modules` helper.
  - The CLI test fixture needed a valid project-local collection-family `templates` mapping.
  - After those fixes, the same focused suite passed with `8 passed`.
- Added duplicate collection-id coverage across families, requiring `family` disambiguation.
- Focused green: `rtk bash scripts/test.bash tests/test_project.py::test_collection_file_read_and_write_text_source tests/test_project.py::test_collection_file_write_can_create_nested_text_source tests/test_project.py::test_collection_file_rejects_path_escape_and_missing_write_target tests/test_project.py::test_collection_file_can_select_duplicate_collection_id_family tests/test_cli.py::test_collection_file_and_edit_cli_read_and_write_descriptor_text tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands tests/test_architecture.py::test_mcp_surface_contract_lists_sdk_owned_tools -q`
  - `9 passed`
- Expanded focused green: `rtk bash scripts/test.bash tests/test_project.py::test_collection_file_read_and_write_text_source tests/test_project.py::test_collection_file_write_can_create_nested_text_source tests/test_project.py::test_collection_file_rejects_path_escape_and_missing_write_target tests/test_cli.py::test_collection_file_and_edit_cli_read_and_write_descriptor_text tests/test_architecture.py tests/test_cli.py::test_frontend_api_cli_outputs_sdk_contract_json -q`
  - `11 passed`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py src/paradev/sdk/__init__.py src/paradev/sdk/frontend_api.py src/paradev/cli.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py src/paradev/surfaces/rest.py tests/test_project.py tests/test_cli.py tests/test_architecture.py`
  - `OK: 10 file(s) - no banned imports`
- `rtk bash scripts/flake.bash --ci`
  - Passed.
- `rtk rg -n "read_collection_file|write_collection_file|collection-file|collection-edit|collection_file|collection_edit|/projects/collections/file|paradev.collection.file.v1|collection.file|collection.edit" src/paradev tests docs/user-manual docs/architecture`
  - Confirmed implementation, tests, and English/Chinese docs.
- `rtk bash scripts/test.bash`
  - `418 passed`
- `rtk uv build`
  - Built `dist/paradev-0.1.0.0.dev0.tar.gz` and `dist/paradev-0.1.0.0.dev0-py3-none-any.whl`.
- `rtk git diff --check`
  - Passed.

## Review

- The operation is text-file scoped and remains inside an existing collection descriptor root.
- Relative paths reject absolute paths, path traversal, empty segments, `.` segments, and backslashes.
- Writes reject missing files unless `create=True`; creation is limited to nested files inside the selected collection descriptor folder.
- Duplicate collection ids across families or source roots require `family` or `source_root` disambiguation.
- The payload includes collection identity, family, source root, file-relative paths, byte size, encoding, exact text, and `written` for mutations.
- Semantic PDX editing, GUI forms, PIHC3 migration, collection scaffold creation, collection removal, and content-aware collection renames remain out of scope.

## Linear

- `TAL-299`: comment `b58b5427-3ee1-456d-807d-33a4b10bb7bd`.
- `TAL-295`: comment `7492b3e1-da2b-429b-95bc-0265552638ce`.
