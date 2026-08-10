# Localization Source Tabs Progress

Date: 2026-06-30 17:10

Linear: ongoing usability goal

## Done

- Replaced secondary localization source tab fallbacks like `loc_zh` with friendly localized language labels.
- Kept the existing generic `loc` tab label unchanged for the primary localization slot.
- Covered Chinese and English rendering so bilingual PIHC3-style source files do not expose internal slot ids in the tab strip.

## Verification

- Red first: `rtk npm --prefix apps/desktop run test:unit -- --run src/moduleEditor/ModuleEntityDetails.test.tsx -t "renders localization language headers as friendly Chinese labels"`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/moduleEditor/ModuleEntityDetails.test.tsx -t "renders localization language headers as friendly Chinese labels"`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/moduleEditor/ModuleEntityDetails.test.tsx src/i18n/locales.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 47840`

## Risks Or Blockers

- Unknown localization language paths still fall back to the existing language detector default, so unusual language folders may need future mapping additions.

## Next

- Continue PIHC3 workflow testing for remaining raw identifiers and source-file picker friction in the module editor.
