# 2026-06-15 14:47 API summary section helper

## Scope

- Added `api_summary_section(...)` as the shared Markdown helper for generated API reference summary sections.
- Routed standard API overview sections through the helper.
- Routed Project object, CLI, MCP, and API catalog custom reference summaries through the helper while preserving every summary bullet and blank line.
- Added focused helper coverage for summary heading layout and deterministic bullet rows.
- Left unrelated desktop, skill, PIHC3, build-loader, HOI4 package, localization-loader, and project-test worktree edits untouched.

## Verification

- `rtk uv run black src/paradev/_api_table_markdown.py src/paradev/sdk/project_api.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py src/paradev/surfaces/api_catalog.py tests/test_api_table.py`: unchanged.
- `rtk uv run python -m py_compile src/paradev/_api_table_markdown.py src/paradev/sdk/project_api.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py src/paradev/surfaces/api_catalog.py tests/test_api_table.py`
- Catalog-wide generated-reference parity check passed for all 29 `API_CATALOG_SOURCE_ROWS` Markdown renderers against tracked manual pages, modulo final newline.
- `rtk bash scripts/test.bash tests/test_api_table.py tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_project_api_table_lists_project_object_surface tests/test_architecture.py::test_cli_api_table_lists_command_contract tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts -q`: 31 passed.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table_markdown.py src/paradev/sdk/project_api.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py src/paradev/surfaces/api_catalog.py tests/test_api_table.py`: OK, 6 files.
- `rtk bash scripts/flake.bash --ci --paths src/paradev/_api_table_markdown.py src/paradev/sdk/project_api.py src/paradev/surfaces/cli.py src/paradev/surfaces/mcp.py src/paradev/surfaces/api_catalog.py tests/test_api_table.py`: unchanged.
- Full test suite deferred to reduce CPU while other migration workers are active.

## Git hygiene

- Stage only the summary-section helper, custom reference summary rollout, helper test, and this note.
- Do not stage `node_modules/`.
