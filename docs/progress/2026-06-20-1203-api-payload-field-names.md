# API Payload Field Names

## Summary

- Named the private API table payload fields for schema, row count, and rows.
- Reused the named fields in table creation, row selection, table copying, and reserved-index validation.
- Kept the public payload keys and API-table behavior unchanged.

## Verification

- `rtk uv run pytest tests/test_api_table.py tests/test_api_table_contracts.py -q`
- `rtk bash scripts/flake.bash --all --paths src/paradev/_api_table.py tests/test_api_table.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table.py tests/test_api_table.py`
- `rtk git diff --check -- src/paradev/_api_table.py docs/progress/2026-06-20-1203-api-payload-field-names.md`
