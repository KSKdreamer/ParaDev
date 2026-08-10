# 2026-06-15 0612 CST - API Catalog Loader Registry

## Scope

- Refactored API catalog payload loading so non-catalog rows resolve through their declared `owner_module` and `table_helper`.
- Kept `API_CATALOG_SOURCE_ROWS` as the single source of truth for generated-reference helper routing.
- Added focused coverage that every catalog source row exposes a callable table helper on its declared owner module.
- Regenerated the Surfaces API reference to reflect the current API catalog source count.

## Boundaries

- Public API catalog schemas, row ids, row counts, and generated API catalog output are unchanged.
- This slice avoids PIHC3 migration files, desktop frontend files, and `node_modules/`.
- Verification is focused on API catalog and Surfaces API generated-reference behavior.
