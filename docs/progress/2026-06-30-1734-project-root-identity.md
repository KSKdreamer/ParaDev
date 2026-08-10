# Project Root Identity Progress

Date: 2026-06-30 17:34

Linear: ongoing usability goal

## Done

- Replaced user-facing `Project ID` rows in Config and Project Management with `Project root`.
- Showed the local project folder path where modders need to orient themselves, while leaving project ids available internally for activation and bridge calls.
- Added English and Chinese copy plus static render coverage for both pages.

## Verification

- Red first: `rtk npm --prefix apps/desktop run test:unit -- --run src/configPage/ConfigPage.test.tsx src/projectManagement/ProjectManagementPage.test.tsx -t "project root instead"`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/configPage/ConfigPage.test.tsx src/projectManagement/ProjectManagementPage.test.tsx src/i18n/locales.test.ts -t "project root instead|locale dictionaries"`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/configPage/ConfigPage.test.tsx src/projectManagement/ProjectManagementPage.test.tsx src/i18n/locales.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 47840`

## Risks Or Blockers

- Internal project ids still appear in DOM ids such as expand/collapse targets, but not as the visible identity row.

## Next

- Wire the Developer rail to the existing surface contract table or remove the placeholder rail item until it is useful.
