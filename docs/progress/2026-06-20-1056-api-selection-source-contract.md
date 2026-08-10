# 2026-06-20 10:56 API selection source contract

## Summary

- Added a contract test that standard `get_*api_selection` helpers delegate to the shared `api_table_selection` helper.
- Left `get_frontend_api_selection` as an explicit manual exception because it supports richer frontend selector shapes, including operation, group, form, and index lookups.
- Avoided dirty generated API docs and PIHC3/desktop work in the main checkout.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk bash scripts/flake.bash --all --paths tests/test_api_table_contracts.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_api_table_contracts.py`
- `rtk git diff --check`
