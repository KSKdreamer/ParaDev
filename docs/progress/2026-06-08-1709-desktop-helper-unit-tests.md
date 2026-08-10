# Desktop Helper Unit-Test Slice

Date: 2026-06-08 17:09 CST

Branch: `codex/scaffold-source-root-selection`

Linear: `TAL-299` comment `79c8859c-ee46-4336-ad6c-1d564ec5ab4c`, `TAL-295` comment `f2932a45-f744-4506-b86d-11e85496e864`

## Summary

This slice made the frontend API helper contract easier to maintain by adding an explicit desktop unit-test gate. The previous selected-action panel-state helper was covered by Python architecture assertions and a production build; now `apps/desktop/src/data/frontendApi.test.ts` directly imports `getFrontendApiActionPanelState(...)` and verifies its behavior against the checked-in generated SDK contract.

This keeps the user-facing model small for HoI4 mod developers: the workbench can choose an action, fill generated fields, request options, confirm writes, and run a planned REST call from one canonical view model. It also gives GUI and SDK developers a fast local test for the same helper before they touch React panels.

## Changes

- Added explicit `vitest` dev dependency and `rtk npm --prefix apps/desktop run test:unit`.
- Added focused unit tests for `getFrontendApiActionPanelState(...)` using `module.create` as a real generated operation fixture.
- Covered default merging, field order, form controls, option request planning, normalize/rest-plan request bodies, stable request keys, confirmation gating, ready Run state, and generated workspace section lookups.
- Updated workflow, UI spec, and English/Chinese user/developer manuals to mention the new unit gate for frontend helper changes.

## Verification

- Red gate first: `rtk npm --prefix apps/desktop run test:unit` failed before implementation because the package had no `test:unit` script.
- `rtk npm --prefix apps/desktop run test:unit -- src/data/frontendApi.test.ts`: passed, 3 tests.
- `rtk npm --prefix apps/desktop run test:unit`: passed, 3 tests.
- `rtk npm --prefix apps/desktop run build`: passed.
- `rtk git diff --check`: passed.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src tests`: passed.
- `rtk bash scripts/flake.bash --ci`: passed.
- `rtk bash scripts/test.bash tests/test_architecture.py -q`: passed, 42 tests.
- `rtk bash scripts/test.bash`: passed, 502 tests.
- `rtk uv build`: passed.
- Browser smoke at `http://127.0.0.1:5174/?smoke=unit-helper-tests`: loaded the ParaDev workbench, found the Run button, and reported 0 browser console errors.

## Review Notes

- The new tests use current SDK-generated operation ids instead of mocks, so they should fail when the Python frontend API contract changes the selected-action panel assumptions.
- `vitest` is a desktop dev dependency only; no Python dependency or generated SDK artifact changed.
- The 15:45 branch-divergence warning remains valid. This branch is still pushed as its own frontend API line and should be reconciled deliberately with `master`.

## Next Work

- Add direct TypeScript tests for option resolution and REST execution helpers if they start carrying more local policy.
- Continue keeping `docs/user-manual/frontend-api.md` and `docs/user-manual/frontend-api-reference.md` aligned with the SDK-owned API list.
- Keep PIHC3 migration assumptions out of `apps/desktop/src/data/frontendApi.ts`; frontend helpers should stay generic over generated operation rows.
