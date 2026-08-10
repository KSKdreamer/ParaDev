# CLI API Catalog Reverse Map

## Summary

- Tightened API catalog CLI coverage so generated base `*-api` CLI commands and their `--markdown` commands must be represented in the API catalog.
- The shared contract helper now checks CLI-to-catalog drift in addition to the existing catalog-to-CLI adapter checks.
- Added a stale-contract regression that injects a `new-api` CLI selector and `new-api --markdown` command without a catalog row.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_cli_commands_flag_unmapped_generated_cli_api_command -q` failed first because unmapped generated CLI API commands were ignored.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_cli_commands_match_cli_api_table tests/test_api_table_contracts.py::test_api_catalog_cli_commands_flag_stale_cli_surface_marker tests/test_api_table_contracts.py::test_api_catalog_cli_commands_flag_unmapped_generated_cli_api_command -q`
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_cli_commands_flag_unmapped_generated_cli_api_command -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk git diff --check`

## Waiver

- Full-suite tests are deferred to keep CPU free for concurrent PIHC3 migration work; this slice changes only API catalog contract tests and one progress note.
