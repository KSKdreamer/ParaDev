# API Catalog CLI Command Contract

## Summary

- Added a contract that ties API catalog CLI metadata to the generated CLI API table.
- The check verifies every catalog row exposing the `cli` surface has both its primary `cli_command` and `markdown_cli_command` represented by `get_cli_api_table()`.
- The check compares CLI row adapters with the catalog selector helper and markdown helper so stale command metadata fails the lightweight API-table contract gate.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_cli_commands_match_cli_api_table -q` failed first because `api_catalog_cli_command_gaps` did not exist.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_cli_commands_match_cli_api_table -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`

## Waiver

- Full-suite tests were skipped to reduce CPU use while PIHC migration work continues; this slice only changes shared API contract tests.
- Full unscoped flake was not run because the previous slice found an unrelated `tests/test_cli.py` Black diff outside these changed files.
