# 2026-06-20 11:01 API row anchor contract

## Summary

- Added focused shared-helper coverage that standard API table rows must retain `doc_page` and `test_anchor` fields.
- Kept production behavior unchanged; this hardens the source-side API table contract that generated user-manual references rely on.
- Avoided dirty generated docs, PIHC3 migration files, and desktop work in the main checkout.

## Verification

- `rtk uv run pytest tests/test_api_table.py tests/test_api_table_contracts.py -q`
- `rtk bash scripts/flake.bash --all --paths tests/test_api_table.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_api_table.py`
- `rtk git diff --check`
