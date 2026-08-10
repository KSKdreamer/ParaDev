# API Selection Table Contract

## Summary

- Added a shared API contract that standard symbol-style API tables list their own `get_*_api_selection` helper.
- Kept project object, CLI, REST, MCP, and frontend selector exceptions explicit because those selectors are documented through non-symbol contract rows or a manual selector path.
- Extended the focused API table contract suite without changing production behavior.

## Verification

- `rtk uv run pytest tests/test_api_table.py tests/test_api_table_contracts.py -q`
- `rtk bash scripts/flake.bash --all --paths tests/test_api_table_contracts.py tests/api_table_contract_helpers.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_api_table_contracts.py tests/api_table_contract_helpers.py`
- `rtk git diff --check -- tests/test_api_table_contracts.py tests/api_table_contract_helpers.py docs/progress/2026-06-20-1252-api-selection-table-contract.md`
