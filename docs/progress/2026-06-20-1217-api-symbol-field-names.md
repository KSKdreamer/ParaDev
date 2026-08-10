# API Symbol Field Names

## Summary

- Named the private API-table symbol and value fields used by the standard symbol row contract.
- Reused the symbol field for standard index, table, and selector defaults.
- Reused the value field for Markdown plain-value rendering while keeping generated output unchanged.

## Verification

- `rtk uv run pytest tests/test_api_table.py tests/test_api_table_contracts.py -q`
- `rtk bash scripts/flake.bash --all --paths src/paradev/_api_table.py src/paradev/_api_table_markdown.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table.py src/paradev/_api_table_markdown.py`
- `rtk git diff --check -- src/paradev/_api_table.py src/paradev/_api_table_markdown.py docs/progress/2026-06-20-1217-api-symbol-field-names.md`
