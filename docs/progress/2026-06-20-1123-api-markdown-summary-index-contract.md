# 2026-06-20 11:23 API Markdown summary index contract

## Summary

- Routed standard API-reference summary counts through `API_STANDARD_INDEXES` instead of repeating `module_index`, `feature_index`, and `kind_index` in `api_summary_lines()`.
- Kept rendered summary text unchanged while sharing the same index order used by API table generation and Markdown index sections.
- Added a focused test with distinct index counts to confirm the summary follows the shared standard index contract.

## Verification

- `rtk uv run pytest tests/test_api_table.py tests/test_api_table_contracts.py -q`
- `rtk bash scripts/flake.bash --all --paths src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk git diff --check -- src/paradev/_api_table_markdown.py tests/test_api_table.py`
