# 2026-06-20 11:28 API Markdown standard index labels

## Summary

- Consolidated standard API Markdown section labels and summary-count labels into one internal `_API_STANDARD_INDEX_LABELS` contract keyed by `API_STANDARD_INDEXES`.
- Kept generated Markdown output unchanged while reducing the number of standard index label maps that future API-table changes must keep aligned.
- Fixed the import-time ordering of the derived section specs so the helper accessors are defined before the tuple is computed.

## Verification

- `rtk uv run pytest tests/test_api_table.py tests/test_api_table_contracts.py -q`
- `rtk bash scripts/flake.bash --all --paths src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk git diff --check -- src/paradev/_api_table_markdown.py tests/test_api_table.py`
