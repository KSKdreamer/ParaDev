# API Markdown List Field Guard Progress

Date: 2026-06-16 11:05 CST

Linear: N/A

## Done

- Added a generated-reference Markdown list-field guard.
- Made malformed scalar list fields fail loudly during API reference table rendering instead of rendering one character per inline-code cell.
- Covered the Markdown row-rendering path in the focused API table helper tests.

## Verification

- `rtk uv run black src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk uv run python -m py_compile src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk bash scripts/test.bash tests/test_api_table.py -q`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_api_catalog_lists_generated_references -q`
- `rtk bash scripts/test.bash tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown -q`
- Generated-reference parity over all 29 `API_CATALOG_SOURCE_ROWS`: no content mismatches, no missing pages; 27 existing non-frontend pages remain trailing-newline-only differences.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk git diff --check -- src/paradev/_api_table_markdown.py tests/test_api_table.py docs/progress/2026-06-16-1105-api-markdown-list-field-guard.md`
- Full suite intentionally deferred to keep CPU free for parallel PIHC3 migration workers.

## Risks Or Blockers

- None known for valid reference rows; only invalid scalar values in configured Markdown list fields now raise `TypeError`.

## Next

- Continue hardening generated API table/reference infrastructure while preserving valid SDK, CLI, REST, MCP, LSP, frontend, and docs output.
