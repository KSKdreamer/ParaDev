# Focus Info Source Label I18n Progress

Date: 2026-06-29 18:16

Linear: TAL-000

## Done

- Localized focus-tree `focus:<id>:info` source selector labels in the module editor.
- Kept English labels unchanged while rendering Chinese labels as `{id} 信息`.
- Added a regression render test for the large source-backed focus selector.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- --run src/moduleEditor/ModuleEntityDetails.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/moduleEditor/ModuleEntityDetails.test.tsx src/i18n/locales.test.ts`
- `rtk npm --prefix apps/desktop run build`
- `rtk git diff --check`
- `PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 rtk bash scripts/run.bash --tauri --port 5197`

## Risks Or Blockers

- This slice only covers focus info source labels; broader module editor string audits should continue.

## Next

- Continue tightening module editor and diagram editor translated copy using real PIHC3 source-backed modules.
