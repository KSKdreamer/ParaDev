# Frontend Binding Index Helper Slice

Date: 2026-06-08 18:07 CST

Branch: `codex/scaffold-source-root-selection`

Linear: `TAL-299` comment `ae927721-a1ca-4275-bdff-ec91ea2cb10d`, `TAL-295` comment `516ea939-e287-40e5-9b81-0d56e5de7dc4`

## Summary

This slice addresses the frontend-facing API maintenance risk called out by the 10:44 and 15:45 alignment reviews by exposing the generated binding reverse index through typed desktop helper APIs. The SDK still owns the canonical operation list and binding metadata; React, codegen, route explorers, and inspector tools now have a stable TypeScript entry point instead of reaching into raw generated JSON.

From a mod developer's perspective, this keeps the workbench mental model small: project, module, build, PDX, LSP, catalog, and surface-contract actions remain one operation catalog. From a frontend developer's perspective, a CLI, MCP, LSP, or REST call key can now resolve back to canonical operation ids through the maintained helper layer.

## Changes

- Added `apps/desktop/src/data/frontendApiBindingIndex.test.ts`.
- Exported `frontendApiBindingIndex`, `FrontendApiBindingSurface`, `FrontendApiBindingIndex`, `buildFrontendApiRestIndexKey(...)`, `getFrontendApiBindingOperationIds(...)`, and `getFrontendApiRestOperationIds(...)` from `apps/desktop/src/data/frontendApi.ts`.
- Covered CLI, REST, MCP, and LSP binding lookups, including stable REST query-key sorting.
- Covered every generated REST binding row against the helper lookup path.
- Updated the English and Chinese frontend API, SDK, and developer manuals to name the binding-index helper surface.
- Updated the UI GUI spec so frontend codegen, inspectors, and route explorers use the helper APIs rather than raw contract JSON.

## Review Items Addressed

- 10:44 review: `TAL-299` is present in `docs/plans/linear.md`, and this branch has a local frontend API progress trail from the initial contract through generated docs, desktop adapters, helper tests, and binding-index guards.
- 10:44 review: the SDK browser source-path contract has already been repaired on this branch in earlier commits; current full Python tests pass.
- 15:45 review: ongoing ParaDev work is staying on `codex/scaffold-source-root-selection`, while PIHC3 migration/template work remains out of this slice.
- 15:45 review: this note keeps the branch divergence risk explicit. The branch still needs an intentional reconciliation with `master`; it should not be blind-merged.

## Progress By Far

- Frontend API contract now covers project create/find/rename/activate/view, module list/create/edit/view, collection source actions, build plan/emit, PDX parse/format, LSP diagnostics/hover/formatting, catalog query, and frontend API meta operations.
- Python SDK tests guard generated summaries, bindings, OpenAPI annotations, source-root semantics, and user-manual examples.
- Desktop tests guard contract loading, helper registries, operation grouping, bridge state, resolver behavior, summary counts, binding-index integrity, and action run state.
- English and Chinese manuals describe CLI and SDK use for HoI4 mod developers, developer-facing extension points, and the maintained frontend API surface.
- Linear planning docs now include `TAL-299`; `TAL-297` remains owned by the PIHC3 migration line rather than shared ParaDev core.

## Verification

- Red gate first: `rtk npm --prefix apps/desktop run test:unit -- src/data/frontendApiBindingIndex.test.ts` failed before implementation because the test file did not exist.
- `rtk npm --prefix apps/desktop run test:unit -- src/data/frontendApiBindingIndex.test.ts`: passed, 4 tests.
- `rtk npm --prefix apps/desktop run test:unit`: passed, 16 tests across 5 files.
- `rtk npm --prefix apps/desktop run build`: passed.
- `rtk git diff --check`: passed.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src tests`: passed, 69 files.
- `rtk bash scripts/flake.bash --ci`: passed.
- `rtk bash scripts/test.bash tests/test_architecture.py -q`: passed, 43 tests.
- `rtk bash scripts/test.bash`: passed, 503 tests.
- `rtk uv build`: passed.
- Browser smoke at `http://127.0.0.1:5174/?smoke=binding-index-helper`: loaded the ParaDev workbench with title `ParaDev` and reported 0 browser console errors.

## Review Notes

- The production behavior change is intentionally small: a typed helper facade around an existing generated index.
- The REST lookup helper normalizes query parameters in sorted key order so generated clients and inspectors can build stable reverse-lookup keys.
- This does not touch PIHC3 migration behavior or add game-specific assumptions to shared core.

## Next Work

- Keep `src/paradev/sdk/frontend_api.py` as the canonical operation source and regenerate artifacts when the contract changes.
- Add new helper tests only where they prevent frontend-only copies of SDK-owned semantics.
- Reconcile `codex/scaffold-source-root-selection` with `master` explicitly before merge, with full Python, desktop, package, and browser verification after reconciliation.
