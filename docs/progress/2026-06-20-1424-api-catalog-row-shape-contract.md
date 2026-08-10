# API Catalog Row Shape Contract

## Summary

- Added a lightweight contract for the aggregate API catalog row schema.
- The check verifies every catalog row exposes the stable text, integer, and list fields consumed by generated SDK, CLI, REST, MCP, and docs references.
- The check allows empty `selector_helper` values, requires non-empty `index_names` and `surfaces`, and guards uniqueness for `id`, `doc_page`, and `markdown_cli_command`.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_rows_have_stable_shape -q` failed first because `api_catalog_row_shape_gaps` did not exist.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_rows_have_stable_shape -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk git diff --check`

## Waiver

- Full-suite tests were skipped to reduce CPU use while PIHC migration work continues; this slice changes only API catalog contract tests and one progress note.
- Full unscoped flake was not run because earlier API catalog slices found an unrelated `tests/test_cli.py` Black diff outside these changed files.
