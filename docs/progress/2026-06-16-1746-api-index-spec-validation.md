# API Index Spec Validation Progress

Date: 2026-06-16 17:46

Linear: n/a

## Done

- Split API indexed-table spec handling into one normalizer and one duplicate/reserved-name validator.
- Preserved existing `api_indexed_table` payload shape, index order, and error messages.

## Verification

- `rtk uv run python -m py_compile src/paradev/_api_table.py tests/test_api_table.py`
- `rtk uv run black src/paradev/_api_table.py tests/test_api_table.py`
- `rtk bash scripts/test.bash tests/test_api_table.py -q`
- `rtk bash scripts/test.bash tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown tests/test_cli.py::test_project_api_cli_outputs_reference_markdown tests/test_cli.py::test_cli_api_cli_outputs_reference_markdown tests/test_cli.py::test_rest_api_cli_outputs_reference_markdown tests/test_cli.py::test_mcp_api_cli_outputs_reference_markdown -q`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_project_api_table_lists_project_object_surface tests/test_architecture.py::test_cli_api_table_lists_command_contract tests/test_architecture.py::test_rest_api_table_lists_openapi_routes tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table.py tests/test_api_table.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/_api_table.py tests/test_api_table.py`
- `rtk git diff --check -- src/paradev/_api_table.py tests/test_api_table.py`

## Risks Or Blockers

- Full-suite testing remains deferred to keep CPU free for the parallel PIHC3 migration work.
- The worktree still contains unrelated PIHC3, desktop, and skill-maintenance changes that were intentionally left untouched.

## Next

- Continue small API/reference helper cleanup only when it does not overlap PIHC3 migration files.
