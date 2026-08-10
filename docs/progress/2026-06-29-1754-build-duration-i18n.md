# Build Duration I18n Progress

Date: 2026-06-29 17:54

Linear: ongoing usability loop

## Done

- Localized visible build-page duration strings for history rows, detail panels, elapsed time, and estimated build time.
- Added matching English and Chinese duration-unit locale keys.
- Added a Chinese build-history regression assertion so `7s` no longer leaks into the translated GUI.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- --run src/buildPage/BuildPage.test.tsx src/i18n/locales.test.ts`
- `rtk npm --prefix apps/desktop run build`
- `rtk git diff --check`
- `PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 rtk bash scripts/run.bash --tauri --port 5194`

## Risks Or Blockers

- Timestamps still use the runtime default `toLocaleString()` output; a future pass should make date/time formatting explicitly locale-aware.

## Next

- Continue the GUI i18n audit outside the build page and address the highest-impact untranslated modder-facing text.
