# Mixed API Indexes Progress

Date: 2026-06-15 09:54

Linear: not linked

## Done

- Generalized `_api_table` index helpers to support custom value fields, list-valued index fields, and explicit empty-key skipping.
- Reused the helper in Project, REST, MCP, CLI, and aggregate API catalog table builders.
- Added focused tests for scalar/list index behavior and custom value-field indexing.
- Left PIHC3 migration, desktop, logo, and `node_modules/` worktree changes untouched.

## Verification

- `rtk uv run python - <<'PY' ...` renderer comparison against `HEAD`: Project, REST, MCP, CLI, and API catalog Markdown renderers matched byte-for-byte.
- `rtk bash scripts/test.bash tests/test_api_table.py tests/test_architecture.py::test_project_api_table_lists_project_object_surface tests/test_architecture.py::test_rest_api_table_lists_openapi_routes tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts tests/test_architecture.py::test_cli_api_table_lists_command_contract tests/test_architecture.py::test_api_catalog_lists_generated_references -q`
- `rtk uv run python -m py_compile src/paradev/_api_table.py src/paradev/surfaces/cli.py src/paradev/surfaces/rest.py src/paradev/surfaces/mcp.py src/paradev/surfaces/api_catalog.py src/paradev/sdk/project_api.py tests/test_api_table.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table.py src/paradev/surfaces/cli.py src/paradev/surfaces/rest.py src/paradev/surfaces/mcp.py src/paradev/surfaces/api_catalog.py src/paradev/sdk/project_api.py tests/test_api_table.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/_api_table.py src/paradev/surfaces/cli.py src/paradev/surfaces/rest.py src/paradev/surfaces/mcp.py src/paradev/surfaces/api_catalog.py src/paradev/sdk/project_api.py tests/test_api_table.py`
- `rtk git diff --check -- src/paradev/_api_table.py src/paradev/surfaces/cli.py src/paradev/surfaces/rest.py src/paradev/surfaces/mcp.py src/paradev/surfaces/api_catalog.py src/paradev/sdk/project_api.py tests/test_api_table.py`

## Risks Or Blockers

- Full-suite tests skipped to keep CPU free for PIHC3 migration workers.
- `gh pr status` reported no open PRs for this checkout, so there were no GitHub review comments to address in this pass.

## Next

- Continue reducing local API-table indexing and Markdown rendering duplication where behavior-equivalence checks remain cheap.
