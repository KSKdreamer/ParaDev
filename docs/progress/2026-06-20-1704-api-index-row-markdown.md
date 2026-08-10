# API Index Row Markdown Contract

## Summary

- Tightened generated Markdown coverage for API reference index rows.
- The reference Markdown contract now verifies each index row renders the expected key, count, and code-formatted value list.
- This protects user-manual API indexes from keeping a visible index key while silently dropping the referenced symbols or reference ids.
- Added a stale-renderer regression that keeps the REST `GET` method index key and count visible but blanks the route-symbol list.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_incomplete_index_row -q` failed first because the Markdown contract only checked index-key presence.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_incomplete_index_row tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_missing_index_key tests/test_api_table_contracts.py::test_api_reference_markdown_matches_renderers -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk git diff --check`

## Waiver

- Full-suite tests are deferred to keep CPU free for concurrent PIHC3 migration work; this slice changes only API table contract tests and one progress note.
