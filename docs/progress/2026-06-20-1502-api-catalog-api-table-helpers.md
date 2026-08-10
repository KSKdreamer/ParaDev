# API Catalog API Table Helper Coverage

## Summary

- Added an aggregate contract that compares every scanned `get_*_api_table` helper against the API catalog.
- The check keeps catalog-only reference rows valid by requiring coverage only for discovered generated API table helpers.
- Added a stale-catalog regression that rewrites the REST table helper and verifies the missing generated helper is reported.
- This tightens the API catalog as the user-facing inventory of SDK, CLI, REST, MCP, and related public surface tables.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_lists_every_generated_api_table_helper -q` failed first because `api_catalog_api_table_helper_gaps` did not exist.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_lists_every_generated_api_table_helper tests/test_api_table_contracts.py::test_api_catalog_api_table_helper_contract_flags_missing_table -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk git diff --check`

## Waiver

- Full-suite tests are deferred to keep CPU free for concurrent PIHC3 migration work; this slice changes only API table contract tests and one progress note.
