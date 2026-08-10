# API Table Schema Contract

## Summary

- Added a generic schema contract for generated API tables.
- The check verifies every API table exposes a non-empty schema string using the `paradev.*.v1` shape.
- The check also enforces schema uniqueness across all generated API tables so downstream clients can treat schema values as stable anchors.
- Added a stale-schema regression that duplicates one table schema and verifies the contract reports the collision.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_tables_have_unique_stable_schemas -q` failed first because `api_table_schema_gaps` did not exist.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_tables_have_unique_stable_schemas tests/test_api_table_contracts.py::test_api_tables_flag_duplicate_schema -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk git diff --check`

## Waiver

- Full-suite tests are deferred to keep CPU free for concurrent PIHC3 migration work; this slice changes only API table contract tests and one progress note.
