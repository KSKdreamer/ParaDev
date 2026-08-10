# API Catalog Index Catalog

## Summary

- Added a contract for the API catalog's documented index catalog rows.
- The check derives required index-catalog IDs from the live catalog table, including direct `rows[*].id`, reference groups, and every top-level `*_index` mapping.
- The check probes each documented Python helper against live sample keys so stale helper names, stale helper arguments, stale table paths, or mismatched lookup behavior fail in the API-table contract gate.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_index_catalog_matches_lookup_helpers -q` failed first because `api_catalog_index_catalog_gaps` did not exist.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_index_catalog_matches_lookup_helpers -q`
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_index_catalog_flags_stale_helper_arguments -q` failed before helper-expression validation was added.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_index_catalog_flags_stale_helper_arguments -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`

## Waiver

- Full-suite tests were skipped to reduce CPU use while other workers continue PIHC migration work; this slice only changes shared API contract tests.
- Full `rtk bash scripts/flake.bash --ci` currently stops on an untouched `tests/test_cli.py` Black diff, so this slice used the scoped `--paths` flake gate for the changed Python files.
