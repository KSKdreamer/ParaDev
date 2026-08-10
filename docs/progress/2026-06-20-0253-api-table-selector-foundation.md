# 2026-06-20 02:53 +0800 - API table selector foundation

## Scope

- Added generic API-table lookup helpers in `paradev._api_table`:
  - `api_table_index_names(table)`
  - `api_table_row(table, key_field, key, row_list_fields=...)`
  - `api_table_index_values(table, index_name, key, index_names=...)`
- Kept this slice internal and behavior-preserving so future CLI/REST/MCP/API-table selectors can reuse one tested lookup path instead of hand-walking rows and indexes.
- Deferred the planned `cli-api` selector surface because `src/paradev/surfaces/cli.py`, `tests/test_architecture.py`, `tests/test_cli.py`, and generated CLI/API catalog docs are already dirty with parallel `module-batch-edit` work.

## Verification

- Red check before implementation: `rtk uv run pytest -q tests/test_api_table.py::test_api_table_index_names_lists_index_payload_keys tests/test_api_table.py::test_api_table_row_returns_detached_row_by_selected_key tests/test_api_table.py::test_api_table_row_rejects_unknown_key_with_choices tests/test_api_table.py::test_api_table_index_values_returns_copied_index_values tests/test_api_table.py::test_api_table_index_values_rejects_unknown_index_and_key` failed on missing helper imports.
- Green focused check: same five tests passed.
- Module check: `rtk uv run pytest -q tests/test_api_table.py` -> 158 passed.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table.py tests/test_api_table.py` -> OK.
- Focused flake check: `rtk bash scripts/flake.bash --ci --paths src/paradev/_api_table.py tests/test_api_table.py` -> unchanged.
- Full suite skipped to preserve CPU while PIHC3 and CLI contract work is active; the new helpers are covered by the shared API-table utility suite.

## Big picture

- This gives the API-table layer a single tested foundation for row selection and index-value selection.
- The next selector surface can be implemented as a thin wrapper around these helpers once the current CLI contract edits settle.
