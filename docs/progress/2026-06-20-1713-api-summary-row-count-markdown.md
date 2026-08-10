# API Summary Row Count Markdown Contract

## Summary

- Tightened generated Markdown coverage for non-catalog API reference summaries.
- The reference Markdown contract now verifies every non-catalog API reference renders the `API rows / API 行数` summary count from table `row_count`.
- This protects user-manual API pages from losing their top-level row-count summary while table rows and indexes remain valid.
- Added a stale-renderer regression that removes the REST API row-count summary line.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_missing_standard_summary_row_count -q` failed first because standard summary row counts were not audited.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_missing_standard_summary_row_count tests/test_api_table_contracts.py::test_api_reference_markdown_matches_renderers -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk git diff --check`

## Waiver

- Full-suite tests are deferred to keep CPU free for concurrent PIHC3 migration work; this slice changes only API table contract tests and one progress note.
