# 2026-06-20 11:52 API summary labels

## Summary

- Replaced the positional `ApiSummaryIndexLabels` tuple alias with a private named tuple for standard API Markdown summary labels.
- Kept generated summary lines unchanged while routing label rendering through `label` and `localized_label` fields.
- Preserved the `API_STANDARD_INDEXES`-driven summary order from the recent API table cleanup series.

## Verification

- `rtk uv run pytest tests/test_api_table.py tests/test_api_table_contracts.py -q`
- `rtk bash scripts/flake.bash --all --paths src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk git diff --check -- src/paradev/_api_table_markdown.py docs/progress/2026-06-20-1152-api-summary-labels.md`
