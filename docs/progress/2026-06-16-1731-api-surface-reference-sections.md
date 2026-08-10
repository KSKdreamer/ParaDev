# API Surface Reference Sections Progress

Date: 2026-06-16 17:31

Linear: N/A

## Done

- Extracted surface-reference Markdown section construction into private helpers.
- Kept `api_surface_reference_markdown` as a compact orchestration wrapper over title/source/regeneration metadata plus generated sections.
- Preserved feature-index inclusion behavior, surface summary counts, generated reference output, and validation timing.
- Avoided active PIHC3 migration, desktop, skill, logo, and `node_modules/` worktree changes.

## Verification

- `rtk uv run python -m py_compile src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk uv run black src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk bash scripts/test.bash tests/test_api_table.py -q`
- `rtk bash scripts/test.bash tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown tests/test_cli.py::test_project_api_cli_outputs_reference_markdown tests/test_cli.py::test_cli_api_cli_outputs_reference_markdown tests/test_cli.py::test_rest_api_cli_outputs_reference_markdown tests/test_cli.py::test_mcp_api_cli_outputs_reference_markdown -q`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_project_api_table_lists_project_object_surface tests/test_architecture.py::test_cli_api_table_lists_command_contract tests/test_architecture.py::test_rest_api_table_lists_openapi_routes tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk git diff --check -- src/paradev/_api_table_markdown.py tests/test_api_table.py`

## Risks Or Blockers

- Full suite deferred to keep CPU available for parallel PIHC3 migration work.
- The shared worktree still contains unrelated dirty and untracked files; this slice did not stage or modify them.

## Next

- Continue keeping generated API references compact, centralized, and covered by targeted renderer tests.
