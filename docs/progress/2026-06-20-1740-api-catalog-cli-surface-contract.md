# API Catalog CLI Surface Contract

## Summary

- Tightened API catalog CLI parity checks so catalog rows with CLI commands must also advertise the `cli` surface.
- The shared contract helper now validates command adapters even when a stale catalog row has dropped the CLI surface marker.
- Added a stale-metadata regression that removes `cli` from the `frontend-api` catalog row while leaving its CLI commands in place.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_cli_commands_flag_stale_cli_surface_marker -q` failed first because rows without `cli` were skipped by the CLI parity helper.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_cli_commands_flag_stale_cli_surface_marker tests/test_api_table_contracts.py::test_api_catalog_cli_commands_match_cli_api_table -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk git diff --check`

## Waiver

- Full-suite tests are deferred to keep CPU free for concurrent PIHC3 migration work; this slice changes only API catalog contract tests and one progress note.
