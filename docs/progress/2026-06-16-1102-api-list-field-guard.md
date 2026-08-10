# API List Field Guard Progress

Date: 2026-06-16 11:02 CST

Linear: N/A

## Done

- Added a shared list-field normalizer for generated API table rows.
- Made malformed scalar list-field values fail loudly in API indexes and copied rows instead of splitting strings into character lists.
- Covered both index and row-copy paths in the focused API table helper tests.

## Verification

- `rtk uv run black src/paradev/_api_table.py tests/test_api_table.py`
- `rtk uv run python -m py_compile src/paradev/_api_table.py tests/test_api_table.py`
- `rtk bash scripts/test.bash tests/test_api_table.py -q`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_api_catalog_lists_generated_references -q`
- `rtk bash scripts/test.bash tests/test_cli.py::test_api_catalog_cli_outputs_table_json -q`
- Generated-reference parity over all 29 `API_CATALOG_SOURCE_ROWS`: no content mismatches, no missing pages; 27 existing non-frontend pages remain trailing-newline-only differences.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table.py tests/test_api_table.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/_api_table.py tests/test_api_table.py`
- `rtk git diff --check -- src/paradev/_api_table.py tests/test_api_table.py docs/progress/2026-06-16-1102-api-list-field-guard.md`
- Full suite intentionally deferred to keep CPU free for parallel PIHC3 migration workers.

## Risks Or Blockers

- None known for valid table rows; only invalid scalar values in configured list fields now raise `TypeError`.

## Next

- Continue hardening generated API table infrastructure while preserving valid SDK, CLI, REST, MCP, LSP, frontend, and docs reference behavior.
