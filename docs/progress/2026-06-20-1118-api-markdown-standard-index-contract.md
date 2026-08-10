# 2026-06-20 11:18 API Markdown standard index contract

## Summary

- Derived the standard generated Markdown index section specs from `API_STANDARD_INDEXES` instead of repeating `module_index`, `feature_index`, and `kind_index`.
- Kept rendered standard API-reference Markdown unchanged while tying table generation and documentation rendering to the same grouping contract.
- Added a focused test that confirms standard Markdown index rows follow the shared table index order and field keys.

## Verification

- `rtk uv run pytest tests/test_api_table.py tests/test_api_table_contracts.py -q`
- `rtk bash scripts/flake.bash --all --paths src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk git diff --check -- src/paradev/_api_table_markdown.py tests/test_api_table.py`
