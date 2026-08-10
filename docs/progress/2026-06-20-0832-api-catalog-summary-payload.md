# 2026-06-20 08:32 API Catalog Summary Payload

## Scope

- Added `ApiCatalogSummary` as a public `paradev.surfaces` TypedDict.
- Added `summary` to `get_api_catalog_table()` with counts for references, indexes, groups, owner modules, surfaces, CLI commands, selector helpers, and doc pages.
- Kept the rendered API catalog summary text behavior stable while sourcing it from the structured table payload.
- Regenerated the affected API catalog and surface facade reference pages.

## Verification

- `rtk git diff --check`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/api_catalog.py src/paradev/surfaces/api.py src/paradev/surfaces/__init__.py`
- `rtk uv run pytest tests/test_architecture.py::test_surfaces_api_table_lists_surface_facade tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_cli.py::test_api_catalog_cli_outputs_table_json tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown`

Full-suite tests were deferred to avoid competing with the active PIHC3 migration work.
