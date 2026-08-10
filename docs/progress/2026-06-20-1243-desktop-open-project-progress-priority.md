# 2026-06-20 12:43 - Desktop Open Project Progress Priority

## Scope

Kept the desktop loading/progress state focused on the user's active open-project action when a background SDK refresh is also running.

## Changes

- Added a regression test for the overlapping `projectOpening` plus `projectLoading` state.
- Updated `appBootProgress` so the post-load open-project handoff takes priority over a background project refresh.

## Verification

- Red regression: `rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts` failed with `Refreshing project` at `82` instead of `Opening project` at `92`.
- Focused green: `rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts` passed.
- Related desktop progress tests: `rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts src/components/AppShell.test.tsx src/components/ProjectPanel.test.tsx src/services/nativeProgress.test.ts` passed.
- Desktop build: `rtk npm --prefix apps/desktop run build` passed, with the existing Vite large-chunk warning.
- Browser smoke: opened `http://127.0.0.1:5174/`; the ParaDev shell loaded the PIHC3 project surface and reported no console errors.

## Notes

The overlapping open-project/refresh state is timing-sensitive in the live UI, so the exact priority rule is locked with a pure `appBootProgress` unit test.
