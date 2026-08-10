# API Reference Heading Contract

## Summary

- Tightened generated API reference Markdown contracts to protect reader-facing section headings.
- The shared contract helper now checks the summary heading, every documented index section heading, and the final API table heading for standard API tables.
- API catalog Markdown checks now protect its catalog-specific reference group, index catalog, index, and table headings.
- Added stale-renderer regressions for a removed REST API feature-index heading and for a future index whose section heading has not been configured.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_missing_section_heading -q` failed first because missing headings were not audited.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_unmapped_index_heading -q` failed first because unmapped index headings were skipped.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_missing_section_heading tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_unmapped_index_heading tests/test_api_table_contracts.py::test_api_reference_markdown_matches_renderers -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk git diff --check`

## Waiver

- Full-suite tests are deferred to keep CPU free for concurrent PIHC3 migration work; this slice changes only API reference contract tests and one progress note.
