# API Catalog Summary Stale Count

## Summary
- Tightened generated API catalog reference markdown checks so the Summary section cannot include duplicate stale count lines.
- Reused the shared summary bullet scanner for all catalog summary count fields.
- Added a stale-contract regression that injects an outdated `References / Reference 数` count beside the correct one.
- Kept runtime behavior unchanged; this slice only strengthens generated API reference documentation contracts.

## Verification
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_stale_catalog_summary_line -q` failed first because duplicate stale catalog summary lines were accepted.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_stale_catalog_summary_line tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_missing_catalog_summary_line tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_missing_catalog_index_count_summary_line tests/test_api_table_contracts.py::test_api_reference_markdown_matches_renderers -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk git diff --check`

## Waiver
- Full-suite tests are deferred to avoid competing with the active PIHC2 to PIHC3 migration workers; this slice used focused API reference contract coverage only.
