# 2026-06-08 05:27 CST - REST Catalog API Bindings

Issues: TAL-299, TAL-295

## Scope

- Added project-scoped REST/OpenAPI bindings for HeavenBase catalog write and refresh:
  - `catalog.write` -> `POST /projects/catalog`
  - `catalog.refresh` -> `PUT /projects/catalog`
- Updated `get_frontend_api_contract()` so frontend agents, generated clients, and the SDK-owned REST request planner can use catalog write/refresh without parsing CLI strings.
- Added FastAPI routes that call the existing SDK/HeavenBase helpers `paradev.hb.catalog_write(...)` and `paradev.hb.catalog_refresh(...)`.
- Updated the frontend API manual, Python SDK manual, developer manual, and architecture boundary in English and Chinese.

## User-Facing Outcome

- GUI and REST clients can now write a new local catalog database with `POST /projects/catalog?path=...` and refresh it with `PUT /projects/catalog?path=...`.
- `frontend-api --operation catalog.write --values-json ... --rest-request --json` now returns a concrete REST request plan:

```json
{
  "method": "POST",
  "path": "/projects/catalog",
  "query": {
    "path": "/workspace/mod",
    "database": "/workspace/mod/.paradev/hb/catalog.sqlite"
  },
  "body": {}
}
```

- Read-only catalog preview/query still use the shared inspection dispatcher; only write/refresh use the mutating `/projects/catalog` resource route.

## Tests And Gates

- Red-first focused tests failed while `/projects/catalog`, catalog REST bindings, and catalog request planning were absent.
- `rtk bash scripts/test.bash tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_frontend_api_surface_bindings_are_machine_readable tests/test_architecture.py::test_frontend_api_rest_request_planner_maps_values_to_query_and_body tests/test_cli.py::test_frontend_api_cli_plans_operation_rest_request_json tests/test_hb.py::test_hb_catalog_write_and_refresh_rest_routes_output_json -q` - `6 passed in 11.62s`
- `rtk uv run --extra rest pytest tests/test_hb.py::test_hb_catalog_write_and_refresh_rest_routes_output_json -q` - `1 passed in 11.42s`
- `rtk uv run paradev frontend-api --operation catalog.write --values-json '{"path":"/workspace/mod","database":"/workspace/mod/.paradev/hb/catalog.sqlite"}' --rest-request --json` - returned `POST /projects/catalog` with query-only parameters.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py src/paradev/surfaces/rest.py tests/test_architecture.py tests/test_cli.py tests/test_hb.py` - `OK: 5 file(s) - no banned imports`
- `rtk bash scripts/flake.bash --ci` - passed
- `rtk bash scripts/test.bash` - `451 passed in 89.20s`
- `rtk uv build` - built `dist/paradev-0.1.0.0.dev0.tar.gz` and `dist/paradev-0.1.0.0.dev0-py3-none-any.whl`

## Review

- Scope stayed on the shared SDK/REST/frontend boundary; no PIHC3 migration or GUI implementation was pulled into this slice.
- The REST routes are thin adapters over existing HeavenBase catalog helpers, preserving SDK ownership of catalog behavior.
- `POST` creates a catalog database and returns `409` for an existing database conflict; `PUT` replaces the catalog via the existing refresh flow.
- SQLite sidecar files may be present during REST writes, so the route test accepts removal of the main database plus WAL/SHM files.

## Linear Sync

- TAL-299 comment: `72f25be7-aefa-4c87-a145-d594e9e94895`
- TAL-295 comment: `7715f077-b8af-48a1-b52a-19c3f0d8d1f4`
