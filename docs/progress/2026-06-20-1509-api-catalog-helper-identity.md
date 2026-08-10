# API Catalog Helper Identity Contract

## Summary

- Tightened the API catalog helper coverage contract to compare resolved callable identity instead of helper names alone.
- Legitimate facade exports remain valid because the check accepts any catalog `owner_module.table_helper` that resolves to the scanned generated API table callable.
- Added a stale-owner regression that points the REST API table row at the API catalog module and verifies the generated REST table helper is reported missing.
- Normalized scanned `__init__.py` source paths to package module names so package-level API helpers are imported through their public module identity.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_api_table_helper_contract_flags_wrong_owner_module -q` failed first because the helper-name-only check missed the stale owner module.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_lists_every_generated_api_table_helper tests/test_api_table_contracts.py::test_api_catalog_api_table_helper_contract_flags_missing_table tests/test_api_table_contracts.py::test_api_catalog_api_table_helper_contract_flags_wrong_owner_module -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk git diff --check`

## Waiver

- Full-suite tests are deferred to keep CPU free for concurrent PIHC3 migration work; this slice changes only API table contract tests and one progress note.
