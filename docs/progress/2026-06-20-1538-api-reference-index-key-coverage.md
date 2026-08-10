# API Reference Index Key Coverage Contract

## Summary

- Added generated-reference coverage for API table index keys.
- The markdown contract now verifies every generated API table index key appears as the first cell of an index table row.
- This protects the reader-facing grouped API tables: feature, module, kind, surface, route, command, and other index sections cannot silently drop a group while the main table remains present.
- Added a stale-renderer regression that removes the REST API `GET` method-index row and verifies the missing `method_index` key is reported.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_missing_index_key -q` failed first because `api_reference_markdown_gaps` only covered row keys and file drift, not index-key rows.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_missing_index_key tests/test_api_table_contracts.py::test_api_reference_markdown_matches_renderers -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk git diff --check`

## Waiver

- Full-suite tests are deferred to keep CPU free for concurrent PIHC3 migration work; this slice changes only API table contract tests and one progress note.
