# 2026-06-15 14:41 API reference intro helper rollout

## Scope

- Routed Project object, CLI, MCP, and API catalog custom reference renderers through `api_reference_intro_lines(...)`.
- Preserved each generated source label, regeneration sentence, command block, blank-line layout, and rendered manual content.
- Added a named API catalog regeneration sentence constant so the renderer call stays compact.
- Left unrelated desktop, skill, PIHC3, build-loader, HOI4 package, localization-loader, and project-test worktree edits untouched.

## Verification

- `rtk uv run black src/paradev/sdk/project_api.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py src/paradev/surfaces/api_catalog.py`: formatted 1 file.
- `rtk uv run python -m py_compile src/paradev/sdk/project_api.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py src/paradev/surfaces/api_catalog.py`
- Catalog-wide generated-reference parity check passed for all 29 `API_CATALOG_SOURCE_ROWS` Markdown renderers against tracked manual pages, modulo final newline.
- `rtk bash scripts/test.bash tests/test_api_table.py tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_project_api_table_lists_project_object_surface tests/test_architecture.py::test_cli_api_table_lists_command_contract tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts -q`: 30 passed.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/project_api.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py src/paradev/surfaces/api_catalog.py`: OK, 4 files.
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/project_api.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py src/paradev/surfaces/api_catalog.py`: unchanged.
- Full test suite deferred to reduce CPU while other migration workers are active.

## Git hygiene

- Stage only the custom reference intro-helper rollout and this note.
- Do not stage `node_modules/`.
