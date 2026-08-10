# Frontend Bridge Unit-Test Slice

Date: 2026-06-08 17:27 CST

Branch: `codex/scaffold-source-root-selection`

Linear: `TAL-299` comment `99717f20-f918-422d-ac9f-0d7a921dd752`, `TAL-295` comment `d0e0895b-3031-4a16-8b11-919760d66bb3`

## Summary

This slice made the desktop helper's dev/offline bridge behavior directly testable. The helper already returned explicit bridge-unavailable result state when Vite dev runs without `VITE_PARADEV_FRONTEND_API_BASE_URL`; now `apps/desktop/src/data/frontendApiBridge.test.ts` proves that relative frontend API and REST execution requests do not call `fetch` in that mode.

From a mod developer's perspective, this keeps the workbench quiet when the REST bridge is not running: panels show a clear unavailable state instead of browser 404 noise. From a GUI developer's perspective, this pins a small but important frontend API invariant: bridge availability and error shaping live in `apps/desktop/src/data/frontendApi.ts`, not in React components.

## Changes

- Added `apps/desktop/src/data/frontendApiBridge.test.ts`.
- Covered relative option, normalize, REST-plan, and REST execution requests in dev/offline mode.
- Asserted that helper resolvers return `Frontend API bridge unavailable` without invoking the supplied fetcher.
- Updated UI spec and English/Chinese manuals to say the desktop unit gate covers bridge-unavailable behavior.

## Verification

- Red gate first: `rtk npm --prefix apps/desktop run test:unit -- src/data/frontendApiBridge.test.ts` failed before implementation because the bridge test file was absent.
- `rtk npm --prefix apps/desktop run test:unit -- src/data/frontendApiBridge.test.ts`: passed, 2 tests.
- `rtk npm --prefix apps/desktop run test:unit`: passed, 8 tests across 3 files.
- `rtk npm --prefix apps/desktop run build`: passed.
- `rtk git diff --check`: passed.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src tests`: passed.
- `rtk bash scripts/flake.bash --ci`: passed.
- `rtk bash scripts/test.bash tests/test_architecture.py -q`: passed, 42 tests.
- `rtk bash scripts/test.bash`: passed, 502 tests.
- `rtk uv build`: passed.
- Browser smoke at `http://127.0.0.1:5174/?smoke=bridge-unit-tests`: loaded the ParaDev workbench, found the execution panel and Run button, and reported 0 browser console errors.

## Review Notes

- This is test and docs coverage only; no production helper behavior changed.
- The test keeps REST bridge availability as helper-owned policy and avoids adding any PIHC3-specific assumptions.
- Browser smoke passed after the broader gates.

## Next Work

- Continue using direct TypeScript tests for frontend helper behavior that affects user-visible state.
- Keep the frontend API manual and developer manual aligned with the generated SDK operation contract.
- Keep branch reconciliation with `master` explicit before merging this frontend API line.
