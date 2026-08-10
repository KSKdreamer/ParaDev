# API Standard Summary Index Counts

## Summary
- Tightened generated standard API reference markdown checks so Summary sections must include standard index count lines, not only `API rows / API 行数`.
- Reused the production `api_summary_lines(...)` helper and parsed each renderer's literal `module_label` from its `api_standard_reference_markdown(...)` call, keeping the contract aligned with renderer source instead of guessing from the page title.
- Added a missing-summary regression that removes the Package API `Package modules / Package 模块数` line.
- Kept runtime behavior unchanged; this slice only strengthens generated API reference documentation contracts.

## Verification
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_missing_standard_summary_index_count -q` failed first because missing standard index summary count lines were accepted.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_missing_standard_summary_index_count tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_missing_standard_summary_row_count tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_stale_standard_summary_row_count tests/test_api_table_contracts.py::test_api_reference_markdown_matches_renderers -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk git diff --check`

## Waiver
- Full-suite tests are deferred to avoid competing with the active PIHC2 to PIHC3 migration workers; this slice used focused API reference contract coverage only.
