# 2026-06-20 10:06 Row source API selection alignment

## Summary

- Updated architecture, catalog, LSP, and PDX API selection tests to source row-count expectations from their public `*_API_TABLE_ROWS` constants.
- Kept generated-reference parity assertions unchanged because these tests already use `heavenbase.utils.load_txt()`.
- Preserved API behavior; this slice only tightens test contracts around the existing API standard tables.

## Verification

- `rtk uv run pytest tests/test_architecture_api_selection.py tests/test_catalog_api_selection.py tests/test_lsp_api_selection.py tests/test_pdx_api_selection.py -q`
