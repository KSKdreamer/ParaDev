# Frontend Resolver Unit-Test Slice

Date: 2026-06-08 17:18 CST

Branch: `codex/scaffold-source-root-selection`

Linear: `TAL-299` comment `23df16b1-7209-4313-9534-02caa5c45080`, `TAL-295` comment `e1608a65-64c3-43cc-85be-00e3f15cc88c`

## Summary

This slice extended the new desktop unit-test gate from selected-action panel state into frontend API request and resolver helpers. The TypeScript helper now has direct tests for the option resolver, normalize resolver, REST-plan resolver, REST execution request builder, and REST execution resolver, all using the checked-in generated SDK operation contract as the source of truth.

For HoI4 mod developers, the visible workflow remains the same: fill generated action fields, resolve dynamic options, review a planned operation, confirm writes, and run the action. For GUI and SDK developers, the request/result states that power that workflow are now pinned by a fast unit gate instead of only by React build smoke.

## Changes

- Added `apps/desktop/src/data/frontendApiResolvers.test.ts`.
- Covered ready and unavailable option request states.
- Covered normalize and REST-plan success plus non-OK error shaping.
- Covered REST execution request URL/query/body construction and ready/error execution result state.
- Updated UI spec and English/Chinese manuals to state that `test:unit` now covers panel-state and request/resolver helpers.

## Verification

- Red gate first: `rtk npm --prefix apps/desktop run test:unit -- src/data/frontendApiResolvers.test.ts` failed before implementation because the resolver test file was absent.
- `rtk npm --prefix apps/desktop run test:unit -- src/data/frontendApiResolvers.test.ts`: passed, 3 tests.
- `rtk npm --prefix apps/desktop run test:unit`: passed, 6 tests across 2 files.
- `rtk npm --prefix apps/desktop run build`: passed.
- `rtk git diff --check`: passed.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src tests`: passed.
- `rtk bash scripts/flake.bash --ci`: passed.
- `rtk bash scripts/test.bash tests/test_architecture.py -q`: passed, 42 tests.
- `rtk bash scripts/test.bash`: passed, 502 tests.
- `rtk uv build`: passed.
- Browser smoke at `http://127.0.0.1:5174/?smoke=resolver-unit-tests`: loaded the ParaDev workbench, found the execution panel and Run button, and reported 0 browser console errors.

## Review Notes

- This is test and docs coverage only; no production helper behavior changed.
- Tests use absolute bridge URLs when they intentionally exercise fetchers, so they do not depend on a live REST bridge or Vite dev/prod bridge-availability mode.
- The helper surface remains generic over generated frontend operation rows and does not add PIHC3-specific assumptions.

## Next Work

- Continue adding unit coverage only where the TypeScript helper carries user-visible policy or error shaping.
- Keep frontend helper docs synchronized with SDK operation rows and the generated frontend API reference.
- Reconcile the frontend API branch with `master` deliberately before merge, as noted in the 2026-06-08 alignment reviews.
