# Localization Language Labels Progress

Date: 2026-06-30 17:01

Linear: ongoing usability goal

## Done

- Replaced raw localization table headers like `l_english` and `l_simp_chinese` with friendly localized language labels.
- Preserved the raw HoI4 language id in each header tooltip and kept table edits keyed by the original language id.
- Added English and Chinese labels for common HoI4 localization languages.

## Verification

- Red first: `rtk npm --prefix apps/desktop run test:unit -- --run src/moduleEditor/ModuleEntityDetails.test.tsx -t "language headers|opens the info page"`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/moduleEditor/ModuleEntityDetails.test.tsx src/i18n/locales.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 47840`

## Risks Or Blockers

- Unknown/custom localization language ids still fall back to the raw id so unusual mods remain editable.

## Next

- Continue deeper PIHC3 workflow testing or move to the next SDK-first GUI alignment gap.
