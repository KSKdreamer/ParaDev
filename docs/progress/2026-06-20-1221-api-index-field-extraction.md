# API Index Field Extraction

## Summary

- Added a private helper for deriving row field names from normalized API index specs.
- Routed indexed table construction through that helper instead of inlining the tuple comprehension.
- Tightened the named-spec test to cover multiple index specs and payload ordering.

## Verification

- `rtk uv run pytest tests/test_api_table.py tests/test_api_table_contracts.py -q`
- `rtk bash scripts/flake.bash --all --paths src/paradev/_api_table.py tests/test_api_table.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table.py tests/test_api_table.py`
- `rtk git diff --check -- src/paradev/_api_table.py tests/test_api_table.py docs/progress/2026-06-20-1221-api-index-field-extraction.md`
