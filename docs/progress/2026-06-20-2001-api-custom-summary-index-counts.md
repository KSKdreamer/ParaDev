# API Custom Summary Index Counts

## Summary

- Tightened generated API reference markdown checks so custom `api_indexed_reference_sections(...)` summary count lines backed by table indexes cannot be silently removed.
- Parsed simple renderer summary f-strings like `len(table["method_index"])` from source, keeping REST/CLI/MCP/project custom summary definitions aligned without hard-coded labels.
- Added a missing-summary regression that removes the REST `Methods / Method` count line and expects the markdown contract helper to report it.
- Fixed renderer source lookup for package modules such as `paradev.hb`, whose API renderer lives in `src/paradev/hb/__init__.py`.

## Verification

- RED: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_missing_custom_summary_index_count -q` failed before the helper change.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_missing_custom_summary_index_count -q`.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_missing_standard_summary_index_count tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_missing_standard_summary_row_count tests/test_api_table_contracts.py::test_api_reference_markdown_matches_renderers -q`.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q` (234 passed).
- GREEN: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`.
- GREEN: `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`.
- GREEN: `rtk git diff --check`.

## Waiver

- Skipped full-suite tests to reduce CPU contention while PIHC2-to-PIHC3 migration work continues; this slice only changes API-reference contract tests.
