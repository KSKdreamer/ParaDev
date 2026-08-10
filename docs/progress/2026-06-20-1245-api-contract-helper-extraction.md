# API Contract Helper Extraction

## Summary

- Moved API contract source scanning and table payload auditing helpers into `tests/api_table_contract_helpers.py`.
- Kept `tests/test_api_table_contracts.py` focused on the contract assertions for selection helpers and auditable API table payloads.
- Preserved the top-level API catalog `id` row-key exception inside the shared helper so future API contract tests reuse the same discovery path.

## Verification

- `rtk uv run pytest tests/test_api_table.py tests/test_api_table_contracts.py -q`
- `rtk bash scripts/flake.bash --all --paths tests/test_api_table_contracts.py tests/api_table_contract_helpers.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_api_table_contracts.py tests/api_table_contract_helpers.py`
- `rtk git diff --check -- tests/test_api_table_contracts.py tests/api_table_contract_helpers.py docs/progress/2026-06-20-1245-api-contract-helper-extraction.md`
