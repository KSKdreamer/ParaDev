# API Reference Title Contract

## Summary

- Tightened generated API reference markdown checks so each top-level title line must match the literal renderer title.
- Parsed `title=` from the shared API reference markdown helper calls used by custom, standard, and surface renderers.
- Added a missing-title regression that removes the REST API Reference H1 and verifies the contract reports the drift.
- Runtime behavior is unchanged; this slice only strengthens the generated API documentation contract.

## Verification

- RED: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_missing_title -q` failed before the helper change.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_missing_title -q`.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_matches_renderers tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_missing_section_heading tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_duplicate_section_heading -q`.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q` with 241 passed.
- GREEN: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`.
- GREEN: `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`.
- GREEN: `rtk git diff --check`.

## Waiver

- Skipped the full suite in this loop to reduce CPU contention while other workers continue the PIHC migration.
