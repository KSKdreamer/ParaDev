# API Unexpected Section Headings

## Summary

- Tightened generated API reference markdown checks so unexpected level-2 section headings are reported directly.
- Added a regression that injects a stale REST reference section before the API standard table and expects an `unexpected section heading` gap.
- Kept existing missing-heading and unmapped-index-heading checks intact.
- Kept runtime behavior unchanged; this slice only strengthens API-reference documentation contracts.

## Verification

- RED: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_unexpected_section_heading -q` failed before the helper change.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_unexpected_section_heading -q`.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_missing_section_heading tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_unmapped_index_heading tests/test_api_table_contracts.py::test_api_reference_markdown_matches_renderers -q`.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q` (239 passed).
- GREEN: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`.
- GREEN: `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`.
- GREEN: `rtk git diff --check`.

## Waiver

- Skipped full-suite tests to reduce CPU contention while PIHC2-to-PIHC3 migration work continues; this slice only changes API-reference contract tests.
