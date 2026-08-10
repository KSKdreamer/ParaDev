# Standard API Table Row Markdown Contract

## Summary

- Tightened generated Markdown coverage for non-catalog API table rows.
- The reference Markdown contract now verifies complete standard table rows instead of accepting any Markdown document that merely mentions each row key.
- Exact row checks use each module's `*_STANDARD_FIELDS` constant when present, then fall back to payload row field order for ordinary symbol tables.
- Added a stale-renderer regression that keeps the `ArchitectureSpec` package API row symbol visible but blanks the final test-anchor cell.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_incomplete_standard_table_row -q` failed first because the Markdown contract only checked row-key presence.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_incomplete_standard_table_row tests/test_api_table_contracts.py::test_api_reference_markdown_matches_renderers -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk git diff --check`

## Waiver

- Full-suite tests are deferred to keep CPU free for concurrent PIHC3 migration work; this slice changes only API table contract tests and one progress note.
