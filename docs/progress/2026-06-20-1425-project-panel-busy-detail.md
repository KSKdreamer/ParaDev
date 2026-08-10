# 2026-06-20 14:25 - Project panel busy detail

## Slice

Made the project panel's live async status name the active project while a desktop open handoff or SDK refresh is running.

## Changes

- Added render expectations for project-specific busy text in `ProjectPanel`.
- Updated the compact progress row to interpolate the active project name for opening and loading states.
- Added English and Chinese locale entries for the project-specific status strings.

## Verification

- Red check: `rtk npm --prefix apps/desktop run test:unit -- src/components/ProjectPanel.test.tsx` failed because the panel still rendered generic `Opening project` and `Loading project registry` text.
- Green check: the same focused command passed with `4 passed`.
- Related async shell suites: `rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts src/components/AppShell.test.tsx src/components/ProjectPanel.test.tsx src/services/nativeProgress.test.ts` passed with `21 passed`.
- Desktop unit suite: `rtk npm --prefix apps/desktop run test:unit` passed with `302 passed`.
- Frontend build: `rtk npm --prefix apps/desktop run build` passed; Vite still reports the existing large-chunk warning.

## Notes

- This keeps the small project-panel progress indicator useful when the boot overlay is not the user's main point of attention.
