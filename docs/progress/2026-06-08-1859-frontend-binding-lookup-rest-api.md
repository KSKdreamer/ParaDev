# Frontend Binding Lookup REST API Slice

Date: 2026-06-08 18:59 CST

Branch: `codex/scaffold-source-root-selection`

Linear: `TAL-299` comment `83dc12d0-512f-4f0d-a51d-54e7028c6f71`, `TAL-295` comment `33a364be-b078-49c9-9e85-1c81cf5190f0`

## Summary

This slice closes REST/OpenAPI and desktop-helper parity for the frontend API binding reverse lookup added in the previous commit. The canonical `surface.frontend_api.binding_lookup` row now has SDK, CLI, REST, generated TypeScript, OpenAPI, and bilingual manual coverage instead of stopping at Python/CLI callers.

From a mod developer's perspective, the CLI remains the shortest path for reverse lookup. From a GUI, REST, or generated-client developer's perspective, the same payload is now available through `GET /frontend-api/binding?binding_surface=...&binding_key=...`, and desktop TypeScript code can build that URL through `buildFrontendApiBindingLookupUrl(...)` instead of hand-maintaining query strings.

## Changes

- Added REST binding metadata `GET /frontend-api/binding` to the canonical `surface.frontend_api.binding_lookup` operation row.
- Added OpenAPI seed coverage for `/frontend-api/binding`, including required `binding_surface` enum and `binding_key` query parameters.
- Added FastAPI route `GET /frontend-api/binding` that delegates to `get_frontend_api_binding_lookup(...)` and returns 400 for unsupported surfaces.
- Extended `plan_frontend_api_rest_request(...)` coverage so binding lookup submitted values produce a REST plan with selector buckets.
- Added desktop helper endpoint path `frontendApiEndpointPaths.binding` and `buildFrontendApiBindingLookupUrl(...)`.
- Regenerated `docs/user-manual/frontend-api-reference.md` and `apps/desktop/src/generated/frontendApi.ts`.
- Updated English and Chinese frontend API, Python SDK, developer, and architecture docs to include the REST binding lookup route and TypeScript URL helper.

## Verification

- Red Python gate first: focused architecture/REST tests failed because `/frontend-api/binding`, the row REST binding, the REST binding index key, REST planning, and the FastAPI route did not exist.
- Red TypeScript gate first: `rtk npm --prefix apps/desktop run test:unit -- src/data/frontendApiBindingIndex.test.ts` failed because `frontendApiEndpointPaths.binding` was undefined.
- `rtk bash scripts/test.bash tests/test_architecture.py::test_openapi_seed_renders_without_runtime_server tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_desktop_frontend_api_helper_exposes_rest_endpoint_helpers tests/test_architecture.py::test_frontend_api_binding_index_maps_surface_calls_to_operation_ids tests/test_architecture.py::test_frontend_api_binding_lookup_helpers_return_operation_ids tests/test_architecture.py::test_frontend_api_contract_indexes_every_surface_binding_and_openapi_annotation tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_typescript_renderer_matches_desktop_contract_file tests/test_architecture.py::test_frontend_api_binding_lookup_rest_route_output_json -q`: passed, 9 tests.
- `rtk npm --prefix apps/desktop run test:unit -- src/data/frontendApiBindingIndex.test.ts src/data/frontendApiSummary.test.ts`: passed, 9 tests.
- `rtk bash scripts/test.bash tests/test_architecture.py tests/test_cli.py tests/test_sdk_examples.py -q`: passed, 105 tests.
- `rtk npm --prefix apps/desktop run test:unit`: passed, 17 tests across 5 files.
- `rtk npm --prefix apps/desktop run build`: passed.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src tests`: passed, 69 files.
- `rtk bash scripts/flake.bash --ci`: passed.
- `rtk uv build`: passed.
- `rtk bash scripts/test.bash`: passed, 506 tests.
- `rtk git diff --check`: passed.

## Review Notes

- The route delegates to the existing SDK helper and does not create a second binding map.
- Query names intentionally match the canonical input names `binding_surface` and `binding_key`, keeping normalize/rest-plan output, OpenAPI parameters, and generated helper code aligned.
- The TypeScript helper only builds the URL; it does not duplicate the lookup logic already available in the generated binding index.
- PIHC3 migration behavior remains untouched.

## Next Work

- Continue keeping REST/OpenAPI, CLI, SDK, TypeScript helper, generated reference, and bilingual manuals in one change whenever a frontend-facing operation row changes.
- Consider a generated helper for read-only frontend API GET meta requests if more GET endpoints need request/result shaping beyond URL construction.
- Keep branch reconciliation with `master` explicit before merge, as noted in the 2026-06-08 alignment reviews.
