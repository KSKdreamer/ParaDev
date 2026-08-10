# 2026-06-20 11:47 API index spec record

## Summary

- Replaced the positional `ApiIndexSpec` tuple alias with a named tuple contract for API table indexes.
- Kept tuple equality and tuple-style input compatibility while routing table builders and Markdown summaries through `index_name` and `field` attributes.
- Added focused coverage for passing an `ApiIndexSpec` instance through `api_indexed_table(...)`.

## Verification

- `rtk uv run pytest tests/test_api_table.py tests/test_api_table_contracts.py -q`
- `rtk bash scripts/flake.bash --all --paths src/paradev/_api_table.py src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table.py src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk git diff --check -- src/paradev/_api_table.py src/paradev/_api_table_markdown.py tests/test_api_table.py docs/progress/2026-06-20-1147-api-index-spec-record.md`
