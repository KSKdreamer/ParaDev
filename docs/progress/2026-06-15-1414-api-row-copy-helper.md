# 2026-06-15 14:14 API row copy helper

## Scope

- Added `copy_api_row(...)` as the shared private copy helper for generated API table rows.
- Made `copy_api_symbol_row(...)` use the shared helper while preserving the standard symbol field order.
- Routed CLI, MCP, Project object, and API catalog table payloads through the helper with explicit list-field copying for mutable list values.
- Removed the four remaining bespoke `_copy_*_row(...)` helpers from those API table modules.
- Added a focused helper test for field order, extra-field omission, and list-field detachment.
- Left unrelated desktop, skill, PIHC3, build-loader, HOI4 package, localization-loader, and project-test worktree edits untouched.

## Verification

- `rtk uv run python -m py_compile src/paradev/_api_table.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py src/paradev/sdk/project_api.py src/paradev/surfaces/api_catalog.py tests/test_api_table.py`
- Generated-reference parity check passed for API catalog, Project object, CLI, and MCP renderers against tracked manual pages, modulo the tracked files' final newline.
- `rtk bash scripts/test.bash tests/test_api_table.py tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_project_api_table_lists_project_object_surface tests/test_architecture.py::test_cli_api_table_lists_command_contract tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts -q`: 27 passed.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py src/paradev/sdk/project_api.py src/paradev/surfaces/api_catalog.py tests/test_api_table.py`: OK, 6 files.
- `rtk bash scripts/flake.bash --ci --paths src/paradev/_api_table.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py src/paradev/sdk/project_api.py src/paradev/surfaces/api_catalog.py tests/test_api_table.py`: unchanged.
- Full test suite deferred to reduce CPU while other migration workers are active.

## Git hygiene

- Stage only the shared row-copy helper, CLI/MCP/Project/API catalog routing, helper tests, and this note.
- Do not stage `node_modules/`.
