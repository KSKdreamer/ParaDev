# API Reference Command Contract

## Summary

- Tightened generated API reference markdown checks so each fenced regeneration command must match the API catalog row for that table helper.
- Derived the expected command from `markdown_cli_command` and `doc_page` instead of adding another manual map.
- Added a stale REST regeneration-command regression that keeps the same docs path but changes the CLI command.
- Runtime behavior is unchanged; this slice only strengthens the generated API documentation contract.

## Verification

- RED: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_stale_regeneration_command -q` failed before the helper change.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_stale_regeneration_command -q`.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_matches_renderers -q`.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q` with 242 passed.
- GREEN: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`.
- GREEN: `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`.
- GREEN: `rtk git diff --check`.

## Waiver

- Skipped the full suite in this loop to reduce CPU contention while other workers continue the PIHC migration.
