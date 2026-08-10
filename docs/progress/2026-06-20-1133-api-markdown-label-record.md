# 2026-06-20 11:33 API Markdown label record

## Summary

- Replaced the positional six-value standard API Markdown label tuple with a private frozen slots dataclass.
- Kept generated API-reference Markdown unchanged while making the standard index title, table labels, and summary labels addressable by name.
- Preserved the shared `API_STANDARD_INDEXES`-keyed label contract from the prior cleanup.

## Verification

- `rtk uv run pytest tests/test_api_table.py tests/test_api_table_contracts.py -q`
- `rtk bash scripts/flake.bash --all --paths src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk git diff --check -- src/paradev/_api_table_markdown.py docs/progress/2026-06-20-1133-api-markdown-label-record.md`
