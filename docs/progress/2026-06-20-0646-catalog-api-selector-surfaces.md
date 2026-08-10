# Catalog API Selector Surfaces

## Scope

- Added a direct REST selector surface for the Catalog API table at `GET /catalog-api`.
- Added a direct MCP selector tool contract for `catalog_api`.
- Kept existing catalog preview/query SDK, CLI, REST inspection, MCP inspection, and LSP behavior unchanged.

## Interface Updates

- Catalog API table row count is now 34, with direct REST and MCP rows for the API-table selector path.
- REST API table row count is now 51, with `GET /catalog-api` grouped under the `catalog` feature.
- MCP API table row count is now 33, with `catalog_api` grouped under the `catalog` feature.
- API catalog reference counts now reflect the updated Catalog, REST, and MCP generated references.

## Verification

- Passed: `rtk uv run --extra dev --extra rest pytest -q tests/test_catalog_api_surface_selectors.py tests/test_catalog_api_selection.py`
- Partial dirty-worktree run passed 21 of 23 selected broad tests; the two failures were unrelated in-progress SDK/CLI count drift already present in the shared workspace.
- Next verification should run from a clean staged worktree built from `HEAD` plus only this slice.
