# API Catalog Reference Group Reader Fields Contract

## Summary

- Added API catalog reference-group validation for reader-facing `title` and `usage` fields.
- The summary/group contract now verifies each reference group has non-empty documentation text, in addition to ids, counts, assignments, and kind summaries.
- This protects the grouped API catalog table from shipping rows that remain technically indexed but lose their reader-facing labels or usage guidance.
- Added a regression that empties one reference group's `title` and `usage` and verifies both fields are reported.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_reference_groups_flag_missing_reader_fields -q` failed first because reference-group `title` and `usage` were not checked.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_summary_and_reference_groups_are_consistent tests/test_api_table_contracts.py::test_api_catalog_reference_groups_flag_missing_reader_fields -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk git diff --check`

## Waiver

- Full-suite tests are deferred to keep CPU free for concurrent PIHC3 migration work; this slice changes only API table contract tests and one progress note.
