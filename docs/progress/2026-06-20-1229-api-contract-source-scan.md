# API Contract Source Scan

## Summary

- Added a shared API source parser for API table contract tests.
- Reused the parsed source metadata across selection-helper presence checks and shared-selector checks.
- Kept the manual frontend selector allowlist and existing assertion behavior unchanged.

## Verification

- `rtk uv run pytest tests/test_api_table.py tests/test_api_table_contracts.py -q`
- `rtk bash scripts/flake.bash --all --paths tests/test_api_table_contracts.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_api_table_contracts.py`
- `rtk git diff --check -- tests/test_api_table_contracts.py docs/progress/2026-06-20-1229-api-contract-source-scan.md`
