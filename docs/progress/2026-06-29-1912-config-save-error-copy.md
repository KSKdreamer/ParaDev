# Config Save Error Copy Progress

Date: 2026-06-29 19:12

Linear: none

## Done

- Changed the config page persistence header so save failures show localized user copy instead of raw config keys or bridge exception text.
- Kept SDK and bridge diagnostics in the existing persistence status object while preventing `persistence.detail` from being rendered directly for error states.
- Removed the raw `paradev.cli.output` hover title from the CLI output select so the shared select uses the localized label instead.
- Added English and Chinese translations for the generic save-failure detail.
- Added regression coverage for raw config keys remaining machine-readable through `data-paradev-config-key` without appearing in visible helper text, tooltips, or persistence alerts.
- Asked a read-only explorer subagent to scan adjacent config-save-failure surfaces; it found no other rendered failure-detail leak and identified the CLI output tooltip fixed in this slice.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- --run src/App.test.ts src/configPage/ConfigPage.test.tsx src/i18n/locales.test.ts`
- `rtk npm --prefix apps/desktop run build`
- `rtk git diff --check`
- `rtk env PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 bash scripts/run.bash --tauri --port 5205`

## Notes

- The Vite production build still reports the existing large-chunk warning.
- `projects/PIHC3` stayed clean after the native Tauri smoke run.
