# 2026-06-20 09:48 HB API reference source alignment

## Summary

- Regenerated `docs/user-manual/hb-api-reference.md` from `paradev hb-api --markdown` so the checked-in HeavenBase facade table includes the current catalog selector export.
- Replaced stale literal HB API row-count assertions with checks derived from `paradev.hb.__all__` and `get_hb_api_table()`.
- Kept the CLI tests focused on verifying JSON and markdown projection behavior while letting the SDK-owned table remain the API reference source of truth.

## Verification

- `rtk uv run pytest tests/test_hb_api_selection.py tests/test_cli.py::test_hb_api_cli_outputs_table_json tests/test_cli.py::test_hb_api_cli_outputs_reference_markdown tests/test_api_catalog_selector_helpers.py -q`
