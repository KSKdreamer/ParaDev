# 2026-06-20 11:57 API index header labels

## Summary

- Replaced the positional private API index header-label tuple with a named tuple for `label`, `count_label`, and `values_label`.
- Kept generated index headers unchanged while routing `api_index_table_header(...)` and `api_index_section(...)` through named fields.
- Continued the API Markdown contract cleanup without touching the dirty API catalog worktree files.

## Verification

- `rtk uv run pytest tests/test_api_table.py tests/test_api_table_contracts.py -q`
- `rtk bash scripts/flake.bash --all --paths src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table_markdown.py tests/test_api_table.py`
- `rtk git diff --check -- src/paradev/_api_table_markdown.py docs/progress/2026-06-20-1157-api-index-header-labels.md`
