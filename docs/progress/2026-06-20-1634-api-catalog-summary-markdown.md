# API Catalog Summary Markdown Contract

## Summary

- Added generated Markdown coverage for the API catalog summary count lines.
- The reference Markdown contract now verifies the top-level reference, layer, feature, kind, and reference-group counts render from `get_api_catalog_table()["summary"]`.
- This protects the user manual overview from losing the aggregate API surface counts while the underlying table and indexes remain valid.
- Added a stale-renderer regression that removes the `References / Reference 数` summary line.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_missing_catalog_summary_line -q` failed first because summary count lines were not audited.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_missing_catalog_summary_line tests/test_api_table_contracts.py::test_api_reference_markdown_matches_renderers -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk git diff --check`

## Waiver

- Full-suite tests are deferred to keep CPU free for concurrent PIHC3 migration work; this slice changes only API table contract tests and one progress note.
