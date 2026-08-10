# 2026-06-20 11:13 API standard index contract

## Summary

- Added an explicit `API_STANDARD_INDEXES` contract for the standard API-table module, feature, and kind indexes.
- Reused the generic `api_indexed_table()` builder inside `api_standard_table()` so standard symbol tables follow the same indexed-table path as custom surface tables.
- Kept generated API-reference behavior unchanged while reducing duplicate index assembly logic.

## Verification

- `rtk uv run pytest tests/test_api_table.py tests/test_api_table_contracts.py -q`
- `rtk bash scripts/flake.bash --all --paths src/paradev/_api_table.py tests/test_api_table.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table.py tests/test_api_table.py`
- `rtk git diff --check -- src/paradev/_api_table.py tests/test_api_table.py`
