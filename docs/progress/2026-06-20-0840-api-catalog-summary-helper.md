# 2026-06-20 08:40 API Catalog Summary Helper

## Scope

- Added `get_api_catalog_summary()` as a public `paradev.surfaces` helper.
- Kept the helper payload detached from table state, matching existing API catalog copy semantics.
- Updated the surface facade API table and regenerated affected generated reference docs.

## Verification

- Red check: focused API catalog/surface tests failed for the missing helper and old generated counts before implementation.
- `rtk git diff --check`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/api_catalog.py src/paradev/surfaces/api.py src/paradev/surfaces/__init__.py`
- `rtk uv run pytest tests/test_architecture.py::test_surfaces_api_table_lists_surface_facade tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_cli.py::test_api_catalog_cli_outputs_table_json tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown`

Full-suite tests were deferred to avoid competing with active PIHC3 migration work.
