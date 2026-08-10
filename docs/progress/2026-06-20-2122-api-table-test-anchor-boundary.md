# API Table Test Anchor Boundary

## Summary

- Tightened API table reference checks so each row `test_anchor` must point to a Python test file under `tests/`.
- Added a REST API regression for an anchor pointing at an existing production function, `src/paradev/cli.py::main`.
- Preserved existing behavior for valid test anchors while preventing API rows from using implementation functions as proof anchors.
- Runtime behavior is unchanged; this slice only strengthens API table contract tests.

## Verification

- RED: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_table_reference_contract_flags_non_tests_anchor -q` failed before the helper change.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_table_reference_contract_flags_non_tests_anchor -q`.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_tables_reference_existing_docs_and_tests -q`.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q` with 246 passed.
- GREEN: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`.
- GREEN: `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`.
- GREEN: `rtk git diff --check`.

## Waiver

- Skipped the full suite in this loop to reduce CPU contention while other workers continue the PIHC migration.
