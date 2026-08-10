# 2026-06-20 10:15 API table contract utility cleanup

## Summary

- Updated `tests/test_api_table_contracts.py` to discover source files with `heavenbase.utils.enum_files()` and read them with `load_txt()`.
- Preserved the existing AST contract: every module exposing a `get_*_api_table` helper must also expose a matching selection helper or use the shared `api_table_selection` path.
- Kept the slice test-only so SDK, CLI, REST, MCP, and generated API reference behavior remain unchanged.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_api_table_contracts.py`
