# API Nested Summary Index Counts

## Summary

- Tightened generated API reference markdown checks so custom summary counts backed by a named index bucket cannot be silently removed.
- Extended the renderer-source parser from whole-index counts like `len(table["method_index"])` to the bounded MCP shape `len(table["mode_index"].get("read", []))`.
- Added a missing-summary regression that removes the MCP `Read tools` count line and expects the markdown contract helper to report the missing `mode_index["read"]` summary.
- Kept runtime behavior unchanged; this slice only strengthens API-reference documentation contracts.

## Verification

- RED: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_missing_custom_summary_index_key_count -q` failed before the helper change.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_missing_custom_summary_index_key_count -q`.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_missing_custom_summary_index_count tests/test_api_table_contracts.py::test_api_reference_markdown_matches_renderers -q`.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q` (235 passed).
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_missing_custom_summary_index_key_count tests/test_api_table_contracts.py::test_api_reference_markdown_matches_renderers -q`.
- GREEN: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`.
- GREEN: `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`.
- GREEN: `rtk git diff --check`.

## Waiver

- Skipped full-suite tests to reduce CPU contention while PIHC2-to-PIHC3 migration work continues; this slice only changes API-reference contract tests.
