# Bilingual API Index Contract

## Summary

- Tightened the user manual API index contract so each API catalog `doc_page` must be linked from both the English and Chinese sections of `docs/user-manual/README.md`.
- The shared API table helper now parses required manual sections before normalizing Markdown links.
- Added a stale-contract regression that removes one API reference link from the Chinese section while leaving the English link intact.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_user_manual_index_contract_flags_missing_chinese_api_reference_link -q` failed first because the manual-index helper only checked the whole README link set.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_user_manual_index_lists_api_catalog_references tests/test_api_table_contracts.py::test_user_manual_index_contract_flags_missing_api_reference_link tests/test_api_table_contracts.py::test_user_manual_index_contract_flags_missing_chinese_api_reference_link -q`
- `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`
- `rtk git diff --check`

## Waiver

- Full-suite tests are deferred to keep CPU free for concurrent PIHC3 migration work; this slice changes only API catalog contract tests and one progress note.
