# API Catalog Reference Group Markdown Contract

## Summary

- Added generated Markdown coverage for API catalog reference-group rows.
- The reference Markdown contract now verifies `get_api_catalog_table()` renders each `reference_groups` row into the dedicated Reference Groups table.
- This protects the user manual from dropping reader-facing group metadata while the payload and selector index still remain valid.
- Added a stale-renderer regression that removes the `overall` Reference Groups row while leaving the `group_index` row intact.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_missing_catalog_group_row -q` failed first because the Markdown contract only covered catalog rows and index keys.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_missing_catalog_group_row tests/test_api_table_contracts.py::test_api_reference_markdown_matches_renderers -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk git diff --check`

## Waiver

- Full-suite tests are deferred to keep CPU free for concurrent PIHC3 migration work; this slice changes only API table contract tests and one progress note.
