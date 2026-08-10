# API Catalog Reference Group Kinds Contract

## Summary

- Added a contract for API catalog reference-group kind summaries.
- The helper now recomputes each `reference_groups[].kinds` list from the referenced catalog rows while preserving the existing first-seen order.
- This keeps the grouped API catalog auditable: module, surface, CLI, REST, MCP, SDK, and other reference groups cannot advertise stale kind coverage.
- Added a stale-summary regression that mutates one reference group to `["stale-kind"]` and verifies the contract reports the drift.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_reference_groups_flag_stale_kind_summary -q` failed first because stale `kinds` values were not checked.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_catalog_summary_and_reference_groups_are_consistent tests/test_api_table_contracts.py::test_api_catalog_reference_groups_flag_stale_kind_summary -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk git diff --check`

## Waiver

- Full-suite tests are deferred to keep CPU free for concurrent PIHC3 migration work; this slice changes only API table contract tests and one progress note.
