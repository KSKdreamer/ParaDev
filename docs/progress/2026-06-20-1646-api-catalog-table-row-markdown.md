# API Catalog Table Row Markdown Contract

## Summary

- Tightened generated Markdown coverage for the main API Catalog table rows.
- The reference Markdown contract now verifies each catalog row renders the expected field order, code cells, plain cells, list cells, and optional selector-helper cell from `get_api_catalog_table()["rows"]`.
- This protects the user manual from retaining a visible reference id while silently dropping schema, helper, surface, doc-page, or test-anchor details.
- Added a stale-renderer regression that keeps the `api-catalog` row id/title prefix but blanks its final test-anchor cell.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_incomplete_catalog_table_row -q` failed first because the Markdown contract only checked row id presence.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_incomplete_catalog_table_row tests/test_api_table_contracts.py::test_api_reference_markdown_matches_renderers -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk git diff --check`

## Waiver

- Full-suite tests are deferred to keep CPU free for concurrent PIHC3 migration work; this slice changes only API table contract tests and one progress note.
