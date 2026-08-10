# API Reference Anchor Contract

## Summary

- Added a focused API table contract that every row's `doc_page` exists and every `test_anchor` names an existing test function.
- Repaired stale API table anchors for catalog, architecture, and PDX rows after test names moved to the current SDK-owned surface terminology.
- Synced the generated user-manual API reference pages for the repaired anchor metadata.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_tables_reference_existing_docs_and_tests -q`
- `rtk uv run pytest tests/test_api_table.py tests/test_api_table_contracts.py tests/test_architecture.py::test_architecture_api_table_lists_public_graph_surface tests/test_architecture.py::test_catalog_api_table_lists_catalog_surfaces tests/test_architecture.py::test_pdx_api_table_lists_parse_format_surfaces -q`
- `rtk bash scripts/flake.bash --all --paths tests/test_api_table_contracts.py tests/api_table_contract_helpers.py src/paradev/hb/__init__.py src/paradev/sdk/architecture.py src/paradev/sdk/pdx.py`
- `rtk git diff --check -- tests/test_api_table_contracts.py tests/api_table_contract_helpers.py src/paradev/hb/__init__.py src/paradev/sdk/architecture.py src/paradev/sdk/pdx.py docs/user-manual/architecture-api-reference.md docs/user-manual/catalog-api-reference.md docs/user-manual/pdx-api-reference.md`

## Waiver

- In the clean scratch worktree created from `HEAD`, `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_api_table_contracts.py tests/api_table_contract_helpers.py src/paradev/hb/__init__.py src/paradev/sdk/architecture.py src/paradev/sdk/pdx.py` reported pre-existing `json`/`pathlib` imports in `src/paradev/hb/__init__.py` and `src/paradev/sdk/pdx.py`. This slice leaves that broader path/serialization refactor out of scope to keep the API anchor repair metadata-only.
