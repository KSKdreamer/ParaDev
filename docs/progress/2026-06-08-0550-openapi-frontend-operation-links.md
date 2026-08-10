# 2026-06-08 05:50 CST - OpenAPI Frontend Operation Links

Issues: TAL-299, TAL-295

## Scope

- Added derived OpenAPI vendor extensions `x-paradev-frontend-api-operation-ids` to REST operations that implement frontend API rows.
- The extension is generated from `get_frontend_api_contract()` row `bindings.rest`, so shared routes such as `GET /projects`, `GET /projects/inspect`, and `POST /projects/build` can be mapped back to stable frontend operation ids without another hand-maintained table.
- Added architecture coverage that verifies every frontend REST binding has an OpenAPI path/method and that every OpenAPI operation id points back to the matching row binding.
- Updated the frontend API, Python SDK, developer, and architecture manuals in English and Chinese.

## User-Facing Outcome

- GUI and codegen agents that start from OpenAPI can now discover canonical operation ids directly from each REST operation.
- Shared endpoints remain understandable:
  - `GET /projects` advertises `project.open` and `project.view`.
  - `GET /projects/inspect` advertises inspection-backed project/module/collection/build/catalog rows.
  - `POST /projects/catalog` advertises `catalog.write`; `PUT /projects/catalog` advertises `catalog.refresh`.

## Tests And Gates

- Red-first focused test failed on missing `x-paradev-frontend-api-operation-ids`.
- `rtk bash scripts/test.bash tests/test_architecture.py::test_openapi_seed_links_rest_operations_to_frontend_api_rows -q` - `1 passed in 0.24s`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_openapi_seed_links_rest_operations_to_frontend_api_rows tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_frontend_api_surface_bindings_are_machine_readable tests/test_architecture.py::test_frontend_api_rest_request_planner_maps_values_to_query_and_body -q` - `5 passed in 0.29s`
- OpenAPI probe confirmed `/projects` GET -> `["project.open", "project.view"]`, `/projects/inspect` GET begins with `["project.inspect", "module.list", "module.view", ...]`, and `/projects/catalog` POST -> `["catalog.write"]`.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/surfaces/rest.py tests/test_architecture.py` - `OK: 2 file(s) - no banned imports`
- `rtk bash scripts/flake.bash --ci` - passed
- `rtk bash scripts/test.bash` - `454 passed in 88.09s`

## Review

- The extension is derived from SDK-owned frontend API rows and does not create a second route registry.
- The invariant covers both directions: frontend REST bindings must be present in OpenAPI, and OpenAPI operation ids must point back to matching REST bindings.
- Scope stayed on frontend-facing API generalizability and codegen support; no GUI or PIHC3 migration behavior was changed.

## Linear Sync

- TAL-299 comment: `9f2421d4-1004-4c62-bae7-06610f155b13`
- TAL-295 comment: `795ab6c9-fe01-4b2e-ad27-73eab8ed31e4`
