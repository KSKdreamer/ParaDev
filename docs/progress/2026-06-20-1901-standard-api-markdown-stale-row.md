# Standard API Markdown Stale Row

## Summary

- Tightened generated standard API reference markdown checks so the API Standard Table cannot include rows whose first-cell API key is not present in the source API table.
- Added a stale-contract regression that injects a complete `STALE /ghost` REST API table row into the rendered reference markdown.
- Kept runtime behavior unchanged; this slice only strengthens generated API reference documentation contracts.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_stale_standard_table_row -q` failed first because stale standard markdown rows were accepted.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_stale_standard_table_row tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_missing_table_row tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_incomplete_standard_table_row tests/test_api_table_contracts.py::test_api_reference_markdown_matches_renderers -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk git diff --check`

## Waiver

- Full-suite tests are deferred to keep CPU free for concurrent PIHC3 migration work; this slice changes generated API reference contract tests and one progress note only.
