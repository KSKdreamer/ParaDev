# API Catalog Summary Count Coverage

## Summary

- Expanded the generated API catalog summary to show every count already present in `get_api_catalog_table()["summary"]`.
- The catalog manual page now includes index, owner module, surface, CLI command, selector helper, and doc page totals alongside the existing reference, layer, feature, kind, and group totals.
- Tightened the Markdown contract helper so those catalog summary lines are protected by generated-reference parity checks.
- Added a stale-renderer regression that removes the catalog index-count summary line.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_missing_catalog_index_count_summary_line -q` failed first because catalog `index_count` summary Markdown was not audited.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_missing_catalog_index_count_summary_line tests/test_api_table_contracts.py::test_api_reference_markdown_matches_renderers -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/api_catalog.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/surfaces/api_catalog.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk git diff --check`

## Waiver

- Full-suite tests are deferred to keep CPU free for concurrent PIHC3 migration work; this slice is limited to API catalog summary rendering, generated docs, and focused API table contract tests.
