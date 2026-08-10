# 2026-06-20 11:41 API index section spec

## Summary

- Replaced the positional `ApiIndexSectionSpec` tuple alias with a named tuple contract for API Markdown index sections.
- Kept existing tuple inputs valid while normalizing renderer internals to named fields.
- Added focused coverage for passing an `ApiIndexSectionSpec` instance through `api_index_sections(...)`.

## Verification

- `rtk uv run pytest tests/test_api_table.py tests/test_api_table_contracts.py -q`
- `rtk bash scripts/flake.bash --all --paths src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk git diff --check -- src/paradev/_api_table_markdown.py tests/test_api_table.py docs/progress/2026-06-20-1141-api-index-section-spec.md`
