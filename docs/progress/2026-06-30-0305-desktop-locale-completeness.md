# Desktop Locale Completeness

## Summary

- Tightened the desktop i18n contract so Chinese is treated as a complete maintained dictionary, not a partial fallback locale.
- Added a unit guard that blocks stale copy describing Chinese as an English fallback.
- Updated the General config-page language help text in English and Chinese.
- Synced the GUI spec and style notes with the no-English-fallback locale contract.
- Launched the Tauri desktop shell with `PARADEV_PROJECTS=projects/PIHC3`; the native app started without runtime errors before the dev session was stopped.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/i18n/locales.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri`
- `rtk git diff --check`

