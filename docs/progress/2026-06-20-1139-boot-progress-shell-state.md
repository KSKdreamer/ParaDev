# 2026-06-20 11:39 - Boot Progress Shell State

## Scope

Tightened the desktop loading/progress UX so the Tauri shell exposes an explicit busy state while the boot overlay blocks interaction.

## Changes

- Added AppShell regression coverage for shell-level boot progress state.
- Added `app-booting` while normal boot progress is visible.
- Added `aria-busy="true"` to the shell only during active boot progress.
- Kept failed boot progress as an alert state instead of marking the shell as still busy.
- Made the rail, project panel, and main workspace inert while any boot overlay is visible so keyboard focus cannot move into stale controls behind the overlay.

## Verification

- Red test first: `rtk npm --prefix apps/desktop run test:unit -- src/components/AppShell.test.tsx` failed on the missing shell busy state.
- Focused green: `rtk npm --prefix apps/desktop run test:unit -- src/components/AppShell.test.tsx` passed after implementation.
- Second red test: the same focused AppShell suite failed on missing inert shell-surface attributes while boot progress was visible.
- Second focused green: the same AppShell suite passed after wiring the shell-surface lock.
- Adjacent startup/progress suites passed:
  - `rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts`
  - `rtk npm --prefix apps/desktop run test:unit -- src/components/ProjectPanel.test.tsx`
  - `rtk npm --prefix apps/desktop run test:unit -- src/services/nativeProgress.test.ts`
- Full desktop unit suite: `rtk npm --prefix apps/desktop run test:unit` passed.
- Desktop build: `rtk npm --prefix apps/desktop run build` passed with the existing Vite large chunk warning.
- Browser smoke: `http://127.0.0.1:5201` rendered the shell, removed the static startup indicator after React mount, showed no boot overlay after load, exposed the project panel/workspace DOM, did not leave loaded shell surfaces inert, and logged no console errors.

## Notes

This gives loading states a stable shell-level contract for accessibility, browser smoke checks, and keyboard interaction blocking while preserving the visible overlay and native progress behavior from the previous slices.
