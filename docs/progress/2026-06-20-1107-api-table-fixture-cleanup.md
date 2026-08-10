# 2026-06-20 11:07 API table fixture cleanup

## Summary

- Reused the local `_api_symbol_row` helper across standard API-table tests instead of repeating the canonical row literal.
- Kept production behavior unchanged; this reduces fixture drift around API row fields, doc pages, and test anchors.
- Avoided dirty generated docs, PIHC3 migration files, and desktop work in the main checkout.

## Verification

- `rtk uv run pytest tests/test_api_table.py tests/test_api_table_contracts.py -q`
- `rtk bash scripts/flake.bash --all --paths tests/test_api_table.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_api_table.py`
- `rtk git diff --check`
