# Config Load Errors Progress

Date: 2026-06-30 18:50

Linear: continuous usability goal

## Done

- Made failed SDK-backed desktop config reads visible in the Config page instead of silently merging `undefined` into local defaults.
- Preserved successful settings while carrying the first failed config key into the existing persistence banner.
- Changed the Config page error banner to show available backend detail and added English/Chinese copy for config load failures.
- Ran a read-only subagent audit for config API/GUI alignment; it found follow-up P1s for no-backend config writes and BuildPage config error swallowing.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- --run src/App.test.ts src/configPage/ConfigPage.test.tsx -t "persistence"` failed before the fix on the missing load-failure status and hidden error detail.
- `rtk npm --prefix apps/desktop run test:unit -- --run src/App.test.ts src/configPage/ConfigPage.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 47840`

## Risks Or Blockers

- Existing Vite production build still reports the large chunk warning.
- Follow-up: no-backend config writes still need to fail visibly instead of pretending a `CM_PARADEV` write succeeded.
- Follow-up: BuildPage still has local catch-and-ignore paths for config reads/writes.

## Next

- Add TDD coverage for no-backend `readConfigValue`/`writeConfigValue` rejection, then route those errors into the Config page save/load banner.
