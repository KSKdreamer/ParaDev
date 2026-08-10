# API Index Shape Contract

## Summary

- Tightened the generic API table payload contract for generated index maps.
- The check now rejects non-string or empty index keys so API table indexes stay JSON-safe and selector-friendly.
- The check also rejects non-string, empty, duplicate, or dangling row ids in index value lists.
- Added regressions that mutate the REST API table method index with a numeric key and a duplicate row id.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_table_payload_contract_flags_non_string_index_keys tests/test_api_table_contracts.py::test_api_table_payload_contract_flags_duplicate_index_values -q` failed first because the payload helper did not report either malformed index shape.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_table_payload_contract_flags_non_string_index_keys tests/test_api_table_contracts.py::test_api_table_payload_contract_flags_duplicate_index_values -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk git diff --check`

## Waiver

- Full-suite tests are deferred to keep CPU free for concurrent PIHC3 migration work; this slice changes only API table contract tests and one progress note.
