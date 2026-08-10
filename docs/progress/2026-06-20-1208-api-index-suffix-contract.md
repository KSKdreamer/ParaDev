# API Index Suffix Contract

## Summary

- Named the private API table index suffix used by index payload discovery.
- Kept index discovery limited to mapping-valued `*_index` payload keys.
- Added a focused assertion that non-mapping `*_index` payload data is ignored.

## Verification

- `rtk uv run pytest tests/test_api_table.py tests/test_api_table_contracts.py -q`
- `rtk bash scripts/flake.bash --all --paths src/paradev/_api_table.py tests/test_api_table.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table.py tests/test_api_table.py`
- `rtk git diff --check -- src/paradev/_api_table.py tests/test_api_table.py docs/progress/2026-06-20-1208-api-index-suffix-contract.md`
