# Manual Stale API Link Contract

## Summary

- Tightened the user manual API index contract so generated `*-reference.md` links in the English and Chinese manual sections must also be present in `get_api_catalog_table()`.
- The shared API table helper now checks manual-to-catalog drift after proving every catalog reference is linked from the manual.
- Added a stale-contract regression that injects a manual-only `stale-api-reference.md` link.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_user_manual_index_contract_flags_stale_api_reference_link -q` failed first because the helper did not report manual-only generated reference links.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_user_manual_index_lists_api_catalog_references tests/test_api_table_contracts.py::test_user_manual_index_contract_flags_missing_api_reference_link tests/test_api_table_contracts.py::test_user_manual_index_contract_flags_missing_chinese_api_reference_link tests/test_api_table_contracts.py::test_user_manual_index_contract_flags_stale_api_reference_link -q`
- `rtk uv run pytest tests/test_api_table_contracts.py::test_user_manual_index_contract_flags_stale_api_reference_link -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk git diff --check`

## Waiver

- Full-suite tests are deferred to keep CPU free for concurrent PIHC3 migration work; this slice changes only API catalog contract tests and one progress note.
