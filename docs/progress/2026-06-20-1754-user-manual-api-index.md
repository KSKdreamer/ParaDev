# User Manual API Index Contract

## Summary

- Added a contract check that every API catalog `doc_page` is linked from `docs/user-manual/README.md`.
- The shared API table test helper now normalizes relative Markdown links in the user manual index to catalog-style `docs/user-manual/*.md` paths.
- Added a stale-contract regression that injects a generated API reference row without a manual index link.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_user_manual_index_lists_api_catalog_references -q` failed first because the manual-index helper did not exist yet.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_user_manual_index_lists_api_catalog_references tests/test_api_table_contracts.py::test_user_manual_index_contract_flags_missing_api_reference_link -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk git diff --check`

## Waiver

- Full-suite tests are deferred to keep CPU free for concurrent PIHC3 migration work; this slice changes only API catalog contract tests and one progress note.
