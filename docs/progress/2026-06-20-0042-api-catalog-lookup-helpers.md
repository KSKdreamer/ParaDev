# API Catalog Lookup Helpers Progress

Date: 2026-06-20 00:42 CST

Linear: N/A

## Done

- Added SDK-owned aggregate API catalog lookup helpers:
  - `get_api_catalog_index_catalog()`
  - `get_api_catalog_reference(reference_id)`
  - `get_api_catalog_reference_ids(index_name, key)`
- Exposed the helpers through the public `paradev.surfaces` facade and regenerated the surfaces facade API table.
- Added an API catalog index catalog section so clients can discover supported groupings without scanning raw rows.
- Regenerated:
  - `docs/user-manual/api-catalog-reference.md`
  - `docs/user-manual/surfaces-api-reference.md`

## Verification

- `rtk bash scripts/test.bash tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_architecture.py::test_api_catalog_helpers_reject_unknown_keys tests/test_architecture.py::test_surfaces_api_table_lists_surface_facade -q`
- `rtk bash scripts/test.bash tests/test_cli.py::test_api_catalog_cli_outputs_table_json tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown tests/test_cli.py::test_surfaces_api_cli_outputs_table_json tests/test_cli.py::test_surfaces_api_cli_outputs_reference_markdown -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/api_catalog.py src/paradev/surfaces/__init__.py src/paradev/surfaces/api.py tests/test_architecture.py tests/test_cli.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/surfaces/api_catalog.py src/paradev/surfaces/__init__.py src/paradev/surfaces/api.py tests/test_architecture.py tests/test_cli.py`
- `rtk git diff --check -- src/paradev/surfaces/api_catalog.py src/paradev/surfaces/__init__.py src/paradev/surfaces/api.py tests/test_architecture.py tests/test_cli.py docs/user-manual/api-catalog-reference.md docs/user-manual/surfaces-api-reference.md`

## Waivers

- Full suite deferred to keep CPU available for parallel PIHC3 migration and frontend workers.

## Next

- Continue moving API reference consumers toward SDK-owned catalog/index helpers instead of row scans.
