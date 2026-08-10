# API Catalog Index Catalog Markdown Contract

## Summary

- Added generated Markdown coverage for API catalog Index Catalog rows.
- The reference Markdown contract now verifies each `index_catalog` row renders its index id, table path, Python helper, and usage text.
- This protects the user manual from retaining a visible index id while silently dropping selector helper or usage details.
- Added a stale-renderer regression that keeps the `surface` Index Catalog row prefix but blanks its usage cell.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_incomplete_catalog_index_catalog_row -q` failed first because the Markdown contract did not inspect full Index Catalog rows.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_incomplete_catalog_index_catalog_row tests/test_api_table_contracts.py::test_api_reference_markdown_matches_renderers -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk git diff --check`

## Waiver

- Full-suite tests are deferred to keep CPU free for concurrent PIHC3 migration work; this slice changes only API table contract tests and one progress note.
