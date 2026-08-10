# Frontend Binding Index Guard Slice

Date: 2026-06-08 17:52 CST

Branch: `codex/scaffold-source-root-selection`

Linear: `TAL-299` comment `7ea3f3e0-cab1-42c7-9e3c-fa0b29c5a379`, `TAL-295` comment `25e4d2f1-4d07-4c03-8294-1d92c4be910f`

## Summary

This slice added an SDK-level guard for the frontend-facing API surface map. The previous slice proved the checked-in TypeScript helper summary registry matches the generated contract; this slice proves the Python SDK contract itself indexes every declared SDK, CLI, REST, MCP, and LSP binding and that every REST binding is mirrored by the matching OpenAPI `x-paradev-frontend-api-operation-ids` annotation.

From a mod developer's perspective, this keeps shared routes such as project open/view, module lists, build, PDX, LSP, catalog, and frontend API meta endpoints discoverable from one operation list. From an adapter/frontend developer's perspective, it prevents a new operation row from being callable but invisible to generated clients that start from `contract["index"]["binding"]`, the CLI/MCP `frontend_operation_ids` slices, or the REST/OpenAPI document.

## Changes

- Added `tests/test_architecture.py::test_frontend_api_contract_indexes_every_surface_binding_and_openapi_annotation`.
- The test recomputes the surface call key for each declared operation binding and asserts that the operation id is present in `get_frontend_api_contract()["index"]["binding"]`.
- The test recomputes the REST operation-id groups from `bindings.rest` and asserts that `get_openapi_seed()` carries identical `x-paradev-frontend-api-operation-ids` values on each matching path/method.
- Updated English and Chinese frontend API manual/developer manual/SDK manual guidance to name the binding-index and OpenAPI annotation guard.
- No production SDK or REST behavior changed; current code already satisfied the invariant.

## Verification

- Red gate first: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_contract_indexes_every_surface_binding_and_openapi_annotation -q` failed before implementation because the test did not exist.
- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_contract_indexes_every_surface_binding_and_openapi_annotation -q`: passed.
- `rtk bash scripts/test.bash tests/test_architecture.py -q`: passed, 43 tests.
- `rtk git diff --check`: passed.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src tests`: passed, 69 files.
- `rtk bash scripts/flake.bash --ci`: passed.
- `rtk npm --prefix apps/desktop run test:unit`: passed, 12 tests across 4 files.
- `rtk npm --prefix apps/desktop run build`: passed.
- `rtk bash scripts/test.bash`: passed, 503 tests.
- `rtk uv build`: passed.
- Browser smoke at `http://127.0.0.1:5174/?smoke=binding-index-guard`: loaded the ParaDev workbench, found Surface Contracts and the Run button, and reported 0 browser console errors.

## Review Notes

- This is test and docs coverage only. It strengthens the SDK-owned frontend API contract without touching PIHC3 migration behavior.
- The guard makes `bindings` the single source of truth for binding reverse indexes and OpenAPI annotations.
- The broader Python, desktop, package, and browser gates passed after the edit.

## Next Work

- Keep adding SDK-level invariants where they prevent parallel GUI/adapter agents from creating hidden surface drift.
- Continue using TypeScript helper tests only for frontend-local view-model behavior.
- Reconcile this branch with `master` explicitly before merge, as noted in the 2026-06-08 alignment reviews.
