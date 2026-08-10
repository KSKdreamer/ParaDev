# API Table Audit Contract

## Summary

- Added a live contract test for every discovered API table helper.
- Verified table row counts, unique row keys, non-empty documentation/test anchors, and index values that point back to table rows.
- Included the top-level API catalog table through its `id` row key so the overall reference inventory is covered alongside standard `get_*api_table()` helpers.

## Verification

- `rtk uv run pytest tests/test_api_table.py tests/test_api_table_contracts.py -q`
- `rtk bash scripts/flake.bash --all --paths tests/test_api_table_contracts.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_api_table_contracts.py`
- `rtk git diff --check -- tests/test_api_table_contracts.py docs/progress/2026-06-20-1238-api-table-audit-contract.md`
