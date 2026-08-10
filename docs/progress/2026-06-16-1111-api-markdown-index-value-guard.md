# API Markdown Index Value Guard Progress

Date: 2026-06-16 11:11 CST

Linear: N/A

## Done

- Added a shared private list-like validator for generated API Markdown rendering.
- Routed API index rows through the validator so malformed scalar index values fail loudly instead of rendering one character per inline-code cell.
- Preserved the existing field-list guard message and added focused index-row regression coverage.

## Verification

- `rtk uv run black src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk uv run python -m py_compile src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk bash scripts/test.bash tests/test_api_table.py -q`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_api_catalog_lists_generated_references -q`
- `rtk bash scripts/test.bash tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown -q`
- `rtk bash scripts/test.bash tests/test_cli.py::test_api_catalog_cli_outputs_table_json -q`
- Generated-reference parity over all 29 `API_CATALOG_SOURCE_ROWS`: no content mismatches, no missing pages; 27 existing non-frontend pages remain trailing-newline-only differences.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk git diff --check -- src/paradev/_api_table_markdown.py tests/test_api_table.py docs/progress/2026-06-16-1111-api-markdown-index-value-guard.md`
- Full suite intentionally deferred to keep CPU free for parallel PIHC3 migration workers.

## Risks Or Blockers

- None known for valid generated API indexes; only invalid scalar values in API Markdown index rows now raise `TypeError`.

## Next

- Continue hardening generated API table/reference infrastructure while preserving valid SDK, CLI, REST, MCP, LSP, frontend, and docs output.
