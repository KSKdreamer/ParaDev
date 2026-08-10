# App Settings Autosave Guard Progress

Date: 2026-06-30 19:16

Linear: continuous usability goal

## Done

- Prevented the desktop GUI from autosaving `paradev.desktop.gui` after the backend app-settings load fails.
- Kept partial desktop config key read failures as visible config-page load errors without blocking normal app-settings persistence.
- Added a focused exported predicate and regression test for the boot/autosave boundary.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- --run src/App.test.ts -t "blocks app settings autosave"` failed before the fix because the guard did not exist.
- `rtk npm --prefix apps/desktop run test:unit -- --run src/App.test.ts -t "blocks app settings autosave"`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/App.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 47840`

## Risks Or Blockers

- Existing Vite production build still reports the large chunk warning.
- Tauri smoke was stopped after launch with Ctrl-C, producing the expected code 130.

## Next

- Continue tightening config and AI/chat UX around visible backend failures, then return to PIHC3 minimization work.
