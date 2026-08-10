# API Catalog Index Catalog Stale Row

## Summary
- Tightened generated API catalog reference markdown checks so the Index Catalog table cannot include rendered rows whose id is absent from `get_api_catalog_table()["index_catalog"]`.
- Reused the shared section-scoped stale-row scanner against the named Index Catalog markdown heading.
- Added a stale-contract regression that injects `stale-index-catalog` into the rendered Index Catalog section.
- Kept runtime behavior unchanged; this slice only strengthens generated API reference documentation contracts.

## Verification
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_stale_catalog_index_catalog_row -q` failed first because stale rendered Index Catalog rows were accepted.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_stale_catalog_index_catalog_row tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_incomplete_catalog_index_catalog_row tests/test_api_table_contracts.py::test_api_reference_markdown_matches_renderers -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk git diff --check`

## Waiver
- Full-suite tests are deferred to avoid competing with the active PIHC2 to PIHC3 migration workers; this slice used focused API reference contract coverage only.
