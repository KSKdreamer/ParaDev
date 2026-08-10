# API Reference Row Coverage Contract

## Summary

- Added generated-reference coverage for API table row keys.
- The markdown contract now verifies every row key from each generated API table appears in its renderer output.
- This closes a docs/API drift gap where a renderer could omit a table row and still keep the generated file synchronized with that incomplete output.
- Added a stale-renderer regression that removes one REST API table row from the rendered markdown and verifies the missing row is reported.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_missing_table_row -q` failed first because `api_reference_markdown_gaps` only reported file drift, not the omitted row.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_missing_table_row -q`
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_matches_renderers -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk git diff --check`

## Waiver

- Full-suite tests are deferred to keep CPU free for concurrent PIHC3 migration work; this slice changes only API table contract tests and one progress note.
