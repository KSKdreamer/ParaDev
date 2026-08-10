# API Catalog Reference Contract

## Summary

- Added a catalog-wide contract that verifies every API catalog row's `markdown_helper` output matches its checked-in `doc_page`.
- Added generated manual reference coverage so every `docs/user-manual/*-reference.md` page is listed by `get_api_catalog_table()`.
- Kept the slice in shared API contract tests to avoid touching the dirty production API catalog and desktop/PIHC work in the main checkout.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_references_match_generated_manual_pages -q` failed first because `api_catalog_reference_gaps` did not exist.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_references_match_generated_manual_pages -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`

## Waiver

- Full-suite tests were skipped to reduce CPU use while other workers are active; this slice only changes API contract tests.
