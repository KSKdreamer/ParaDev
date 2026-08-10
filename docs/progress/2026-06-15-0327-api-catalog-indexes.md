# 2026-06-15 03:27 API Catalog Indexes

## Summary

- Added `owner_module_index` and `surface_index` to the aggregate API catalog table.
- Regenerated [API Catalog Reference](../user-manual/api-catalog-reference.md) with owner-module and surface index sections.
- Updated maintainer docs and focused CLI/architecture tests so module ownership and surface coverage audits do not require ad hoc row filtering.

## Verification

- `rtk uv run python -m py_compile src/paradev/surfaces/api_catalog.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_cli.py::test_api_catalog_cli_outputs_table_json tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown tests/test_cli.py::test_api_catalog_cli_rejects_markdown_json_combo -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/api_catalog.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/surfaces/api_catalog.py tests/test_architecture.py tests/test_cli.py`
- `rtk git diff --check -- <intentional API catalog index files>`
