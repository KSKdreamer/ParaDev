# 2026-06-20 11:16 - Project Picker Progress

## Scope

Improved the desktop project picker loading state so PIHC3 users get a visible, live progress indicator while the SDK project registry refreshes or the shell is opening the active project.

## Changes

- Added a `role="status"` project-picker progress row for project loading/opening states.
- Kept the project path/error line visible while the busy row reports the current async state.
- Added compact pulse styling for the project-picker progress row, reusing the boot progress animation.
- Added a static React render test for the loading indicator contract.

## Verification

- Red test first: `rtk npm --prefix apps/desktop run test:unit -- src/components/ProjectPanel.test.tsx -t "shows a live project progress indicator"` failed on the missing `project-picker-progress` row.
- `rtk npm --prefix apps/desktop run test:unit -- src/components/ProjectPanel.test.tsx -t "shows a live project progress indicator"`
- `rtk npm --prefix apps/desktop run test:unit -- src/components/ProjectPanel.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke on `http://127.0.0.1:5201/`: loaded the desktop shell, confirmed the project panel and picker render, saw no Vite error overlay, and saw zero warning/error console logs.
- `rtk git diff --check -- apps/desktop/src/components/ProjectPanel.tsx apps/desktop/src/components/ProjectPanel.test.tsx apps/desktop/src/styles/app.css`

## Notes

Plain Vite still cannot exercise the exact Tauri-backed project loading handoff, so the busy-row behavior is covered by the static React test. The browser smoke verifies the surrounding desktop shell still renders cleanly.

The Vite production build still emits the existing large-chunk warning for editor bundles.
