# Build History Timestamp I18n Progress

Date: 2026-06-29 18:01

Linear: ongoing usability loop

## Done

- Replaced host-default build-history timestamp rendering with translator-owned timestamp patterns.
- Added English and Chinese timestamp format keys.
- Added a Chinese regression assertion so build history no longer renders AM/PM timestamps in the translated GUI.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- --run src/buildPage/BuildPage.test.tsx src/i18n/locales.test.ts`
- `rtk npm --prefix apps/desktop run build`
- `rtk git diff --check`
- `PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 rtk bash scripts/run.bash --tauri --port 5195`

## Risks Or Blockers

- This formats build history timestamps with local time components; broader date/time localization for other surfaces still needs audit.

## Next

- Use the parallel GUI/i18n audit results to pick the next non-build-page translated shell improvement.
