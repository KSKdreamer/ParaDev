# API Table Row Header Guards Progress

Date: 2026-06-16 11:21 CST

Linear: N/A

## Done

- Routed direct generated-reference `table_row(...)` and `table_header(...)` calls through the shared Markdown list-like validator.
- Preserved valid generated table output while making malformed scalar cells and labels fail loudly.
- Added focused helper coverage for scalar table-row and table-header inputs.

## Verification

- `rtk uv run black src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk uv run python -m py_compile src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk bash scripts/test.bash tests/test_api_table.py -q`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_api_catalog_lists_generated_references -q`
- `rtk bash scripts/test.bash tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown -q`
- `rtk bash scripts/test.bash tests/test_cli.py::test_api_catalog_cli_outputs_table_json -q`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_project_inspection_reference_lists_contract_indexes -q`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_surface_contract_catalog_lists_static_boundaries -q`
- `rtk bash scripts/test.bash tests/test_cli.py::test_architecture_cli_outputs_surface_contract_reference_markdown -q`
- `rtk bash scripts/test.bash tests/test_cli.py::test_inspections_cli_outputs_reference_markdown -q`
- Generated-reference parity over all 29 `API_CATALOG_SOURCE_ROWS`: no content mismatches, no missing pages; 27 existing non-frontend pages remain trailing-newline-only differences.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk git diff --check -- src/paradev/_api_table_markdown.py tests/test_api_table.py docs/progress/2026-06-16-1121-api-table-row-header-guards.md`
- Full suite intentionally deferred to keep CPU free for parallel PIHC3 migration workers.

## Risks Or Blockers

- None known for valid generated reference rows; only invalid scalar inputs passed directly to `table_row(...)` or `table_header(...)` now raise `TypeError`.

## Next

- Continue hardening generated API table/reference infrastructure while preserving valid SDK, CLI, REST, MCP, LSP, frontend, and docs output.
