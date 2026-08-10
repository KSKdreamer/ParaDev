# API Summary Extra Lines

## Summary

- Tightened generated API reference markdown checks so unexpected extra bullets in the `Summary / 汇总` section are reported instead of relying on broad file-output drift.
- Added surface-reference summary support for renderers that use `api_surface_reference_markdown(...)`, covering `surface_index` and optional `feature_index` counts.
- Added regressions for an injected stale REST summary bullet and a missing Catalog API surface summary count.
- Kept runtime behavior unchanged; this slice only strengthens generated API reference documentation contracts.

## Verification

- RED: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_unexpected_summary_line -q` failed before the unexpected-summary helper change.
- RED: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_missing_surface_summary_index_count -q` failed before the surface-summary helper change.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_unexpected_summary_line tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_missing_surface_summary_index_count -q`.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_matches_renderers tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_stale_standard_summary_row_count tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_missing_custom_summary_literal -q`.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q` (238 passed).
- GREEN after formatting: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_unexpected_summary_line tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_missing_surface_summary_index_count tests/test_api_table_contracts.py::test_api_reference_markdown_matches_renderers -q`.
- GREEN: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`.
- GREEN: `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`.
- GREEN: `rtk git diff --check`.

## Waiver

- Skipped full-suite tests to reduce CPU contention while PIHC2-to-PIHC3 migration work continues; this slice only changes API-reference contract tests.
