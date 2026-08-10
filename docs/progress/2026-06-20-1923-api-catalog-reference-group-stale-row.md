# API Catalog Reference Group Stale Row

## Summary
- Tightened generated API catalog reference markdown checks so the Reference Groups table cannot include rendered rows whose group id is absent from `get_api_catalog_table()["reference_groups"]`.
- Named the catalog-only markdown headings used by the contract helper before reusing the shared stale-row scanner.
- Added a stale-contract regression that injects `stale-reference-group` into the rendered Reference Groups section.
- Kept runtime behavior unchanged; this slice only strengthens generated API reference documentation contracts.

## Verification
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_stale_catalog_group_row -q` failed first because stale rendered reference-group rows were accepted.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_stale_catalog_group_row tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_missing_catalog_group_row tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_incomplete_catalog_group_row tests/test_api_table_contracts.py::test_api_reference_markdown_matches_renderers -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk git diff --check`

## Waiver
- Full-suite tests are deferred to avoid competing with the active PIHC2 to PIHC3 migration workers; this slice used focused API reference contract coverage only.
