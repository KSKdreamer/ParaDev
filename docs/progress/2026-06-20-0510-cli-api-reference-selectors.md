# 2026-06-20 05:10 - CLI API Reference Selectors

## Slice

- Added standard `--symbol` and `--index/--key` selectors to generated `*-api` CLI reference commands.
- Routed those commands through the catalog-declared selector helpers instead of table-only helpers.
- Updated the generated CLI API reference from a clean staged-index render so unrelated module-batch work stayed unstaged.

## Verification

- `rtk uv run pytest -q tests/test_cli_api_reference_selectors.py`
- `rtk uv run pytest -q tests/test_cli_api_reference_selectors.py tests/test_api_table_contracts.py`
- Broad legacy architecture assertions still hard-code pre-selector CLI/catalog row counts and were not updated in this slice.
