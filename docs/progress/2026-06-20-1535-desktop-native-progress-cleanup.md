# 2026-06-20 15:35 - Desktop native progress cleanup

## Summary

Fixed a desktop progress edge case in the Tauri shell. The React app now explicitly clears the native window progress bar during app teardown, so a window close/reload cannot leave stale OS-level progress visible after boot progress was active.

This keeps the visible boot overlay, Tauri native progress bar, and app lifecycle aligned for long PIHC3 project loads.

## Changed

- Added `clearNativeBootProgress(...)` to the desktop native progress service.
- Added an app-level unmount cleanup effect that clears native progress and logs cleanup failures without blocking teardown.
- Added a native progress regression test for the teardown clear path.

## Verification

- Red test first: `rtk npm --prefix apps/desktop run test:unit -- src/services/nativeProgress.test.ts` failed because `clearNativeBootProgress` did not exist.
- `rtk npm --prefix apps/desktop run test:unit -- src/services/nativeProgress.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts src/services/nativeProgress.test.ts src/components/AppShell.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk git diff --check -- apps/desktop/src/App.tsx apps/desktop/src/services/nativeProgress.ts apps/desktop/src/services/nativeProgress.test.ts`

Note: Vite still reports existing large chunk warnings during build; the build exits successfully and this slice does not change chunking.
