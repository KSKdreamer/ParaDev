# 2026-06-20 14:28 - Nonblocking boot error

## Slice

Kept failed desktop startup progress visible without trapping the user behind an inert shell.

## Changes

- Added an AppShell regression test that failed boot progress remains an alert but does not hide or inert the rail, project panel, or main shell.
- Updated shell blocking so normal loading progress still blocks interaction, while error progress is non-blocking.
- Changed error progress styling from a full-screen blurred overlay to a non-blocking alert toast.

## Verification

- Red check: `rtk npm --prefix apps/desktop run test:unit -- src/components/AppShell.test.tsx` failed because failed boot progress still made the rail, project panel, and main shell inert.
- Green check: the same focused command passed with `8 passed`.
- Related async shell suites: `rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts src/components/AppShell.test.tsx src/components/ProjectPanel.test.tsx src/services/nativeProgress.test.ts` passed with `22 passed`.
- Desktop unit suite: `rtk npm --prefix apps/desktop run test:unit` passed with `303 passed`.
- Frontend build: `rtk npm --prefix apps/desktop run build` passed; Vite still reports the existing large-chunk warning.

## Notes

- Users can now use visible controls after an initial SDK load failure instead of being left behind an unrecoverable error overlay.
