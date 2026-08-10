# API Markdown Stale Index Row

## Summary
- Tightened generated API reference markdown checks so index sections cannot contain rendered rows whose first-cell index key is absent from the source API table.
- Reused the existing section-row scanner for both standard and catalog index headings.
- Added a stale-contract regression that injects `STALE_METHOD` into the REST Method Index markdown.
- Kept runtime behavior unchanged; this slice only strengthens generated API reference documentation contracts.

## Verification
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_stale_index_row -q` failed first because stale rendered index rows were accepted.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_stale_index_row tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_missing_index_key tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_incomplete_index_row tests/test_api_table_contracts.py::test_api_reference_markdown_matches_renderers -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk git diff --check`

## Waiver
- Full-suite tests are deferred to avoid competing with the active PIHC2 to PIHC3 migration workers; this slice used focused API reference contract coverage only.
