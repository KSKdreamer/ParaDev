# API Summary Stale Row Count

## Summary
- Tightened generated standard API reference markdown checks so the Summary section cannot include a duplicate stale `API rows / API 行数` count.
- Added a section-scoped summary bullet scanner for future generated-summary parity checks.
- Added a stale-contract regression that injects an outdated REST API row-count summary line beside the correct one.
- Kept runtime behavior unchanged; this slice only strengthens generated API reference documentation contracts.

## Verification
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_stale_standard_summary_row_count -q` failed first because duplicate stale row-count summary lines were accepted.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_stale_standard_summary_row_count tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_missing_standard_summary_row_count tests/test_api_table_contracts.py::test_api_reference_markdown_matches_renderers -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk git diff --check`

## Waiver
- Full-suite tests are deferred to avoid competing with the active PIHC2 to PIHC3 migration workers; this slice used focused API reference contract coverage only.
