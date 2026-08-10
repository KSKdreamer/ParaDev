# API Catalog Reference Group Full Row Contract

## Summary

- Tightened generated Markdown coverage for API catalog reference-group rows.
- The reference Markdown contract now expects each Reference Groups table row to include the group id, title, reference count, kind list, reference id list, and usage text.
- This protects the user manual from retaining a visible group row while silently dropping the grouped API table details readers need.
- Added a stale-renderer regression that keeps the `overall` group row prefix but blanks its usage cell.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_incomplete_catalog_group_row -q` failed first because the Markdown contract only checked the group id/title prefix.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_incomplete_catalog_group_row tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_missing_catalog_group_row tests/test_api_table_contracts.py::test_api_reference_markdown_matches_renderers -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk git diff --check`

## Waiver

- Full-suite tests are deferred to keep CPU free for concurrent PIHC3 migration work; this slice changes only API table contract tests and one progress note.
