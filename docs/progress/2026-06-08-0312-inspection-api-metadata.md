# Inspection Frontend API Metadata

Date: 2026-06-08 03:12 CST

Issues: TAL-299, TAL-293, TAL-295

## Summary

- Added concrete REST, MCP, and payload metadata for inspection-backed frontend API rows.
- Standardized module, collection, read-only build, and read-only catalog rows on the shared `Project.inspect(kind, **filters)` dispatcher.
- Documented REST `GET /projects/inspect?kind=...` and MCP `project_inspect` bindings for those rows.
- Added explicit payload schema names such as `paradev.build.modules.v1`, `paradev.build.summary.v1`, `paradev.build.graph.v1`, and `paradev.hb.catalog-preview.v1`.
- Updated the bilingual frontend API manual, bilingual developer manual, and architecture interface map.

## Tests

- Red: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations -q`
  - Failed before implementation because inspection-backed rows did not consistently publish concrete REST, MCP, and payload metadata.
- Focused green: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations -q`
  - `1 passed`
- Focused surface green: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_mcp_surface_contract_lists_sdk_owned_tools -q`
  - `3 passed`
- Contract probe:
  - Confirmed `module.list -> GET /projects/inspect?kind=modules`, MCP `project_inspect`, payload `paradev.build.modules.v1`.
  - Confirmed `build.summary -> GET /projects/inspect?kind=summary`, MCP `project_inspect`, payload `paradev.build.summary.v1`.
  - Confirmed `build.graph -> GET /projects/inspect?kind=build-graph`, MCP `project_inspect`, payload `paradev.build.graph.v1`.
  - Confirmed `catalog.preview -> GET /projects/inspect?kind=catalog-preview`, MCP `project_inspect`, payload `paradev.hb.catalog-preview.v1`.
  - Confirmed `catalog.query -> GET /projects/inspect?kind=catalog-query`, MCP `project_inspect`, payload `paradev.hb.catalog-query.v1`.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py`
  - `OK: 2 file(s) - no banned imports`
- `rtk rg -n 'GET /projects/inspect\?kind=summary|paradev\.build\.summary\.v1|paradev\.build\.modules\.v1|paradev\.hb\.catalog-preview\.v1|project_inspect|inspection-backed|Project\.inspect\(kind' docs/user-manual docs/architecture/interfaces.md src/paradev/sdk/frontend_api.py tests/test_architecture.py`
  - Confirmed source/docs/test coverage for the maintained metadata.
- `rtk bash scripts/flake.bash --ci`
  - Passed.
- `rtk bash scripts/test.bash`
  - `441 passed`
- `rtk uv build`
  - Built `dist/paradev-0.1.0.0.dev0.tar.gz` and `dist/paradev-0.1.0.0.dev0-py3-none-any.whl`.
- `rtk git diff --check`
  - Passed.

## Review

- The API surface stays generic: read panels reuse `Project.inspect(...)` instead of adding bespoke REST or MCP operations.
- Frontend callers can use the operation row payload field to pick the concrete schema for each inspection `kind`.
- The generic `project.inspect` row keeps the broader `Project inspection payload` label because the exact schema depends on `kind`.
- `catalog.query` remains read-only over an existing written or refreshed local catalog database.

## Linear

- `TAL-299`: comment `5ac01d44-8c32-4b71-87f0-af84ff346599`.
- `TAL-293`: comment `bc65f131-5b5f-4ff9-9d17-dc0473b38713`.
- `TAL-295`: comment `95ab1b94-e5be-46e2-8aea-8879b48dfa6f`.
