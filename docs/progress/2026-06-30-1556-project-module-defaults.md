# Project Module Defaults Progress

Date: 2026-06-30 15:56

Linear: ongoing usability goal

## Done

- Made desktop-only module default sizes persist by project instead of one global list.
- Kept SDK-backed thumbnail cache size on the desktop config-value bridge instead of folding it into project-local GUI settings.
- Preserved legacy `configPage.moduleDefaults` payloads as fallback rows for the default project.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- --run src/App.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/App.test.ts src/configPage/ConfigPage.test.tsx src/components/AppShell.test.tsx`
- `rtk npm --prefix apps/desktop run build`
- `rtk npm --prefix apps/desktop run test:unit -- --run`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 47840`

## Risks Or Blockers

- The app settings schema name is unchanged; the normalizer handles the old module-default list as a migration fallback.

## Next

- TDD the floating chat route display so gateway/provider/model labels are localized and not raw-only backend IDs.
