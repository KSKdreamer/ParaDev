# API Markdown Payload Fields

## Summary

- Named the private API Markdown payload fields for row count and table rows.
- Reused those names in field labels, row extraction, and summary rendering.
- Kept generated Markdown output and public helper behavior unchanged.

## Verification

- `rtk uv run pytest tests/test_api_table.py tests/test_api_table_contracts.py -q`
- `rtk bash scripts/flake.bash --all --paths src/paradev/_api_table_markdown.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table_markdown.py`
- `rtk git diff --check -- src/paradev/_api_table_markdown.py docs/progress/2026-06-20-1212-api-markdown-payload-fields.md`
