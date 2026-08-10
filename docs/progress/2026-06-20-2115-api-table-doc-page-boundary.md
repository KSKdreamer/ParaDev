# API Table Doc Page Boundary

## Summary

- Tightened API table reference checks so each row `doc_page` must be an existing markdown file under `docs/`.
- Added a REST API regression for a row pointing at root `README.md`, which exists but is outside the docs contract.
- Preserved current valid API rows that point at either `docs/user-manual/` or `docs/architecture/`.
- Runtime behavior is unchanged; this slice only strengthens API table contract tests.

## Verification

- RED: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_table_reference_contract_flags_non_docs_doc_page -q` failed before the helper change.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_table_reference_contract_flags_non_docs_doc_page -q`.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_tables_reference_existing_docs_and_tests -q`.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q` with 245 passed.
- GREEN: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`.
- GREEN: `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`.
- GREEN: `rtk git diff --check`.

## Waiver

- Skipped the full suite in this loop to reduce CPU contention while other workers continue the PIHC migration.
