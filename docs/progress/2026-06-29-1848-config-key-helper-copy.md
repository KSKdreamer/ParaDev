# Config Key Helper Copy Progress

Date: 2026-06-29 18:48

Linear: N/A

## Done

- Replaced visible `paradev.*` helper text in config fields with localized user-facing copy.
- Added `data-paradev-config-key` to the CLI output and build parallelism controls so the SDK/CM_PARADEV contract remains machine-readable.
- Replaced the default config persistence badge copy from `CM_PARADEV` to localized saved-state text.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- --run src/configPage/ConfigPage.test.tsx src/i18n/locales.test.ts`
- `rtk git diff --check`
- `rtk npm --prefix apps/desktop run build`
- `PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 rtk bash scripts/run.bash --tauri --port 5201`

## Risks Or Blockers

- Live backend status detail text can still surface raw bridge messages; that should be normalized separately because it crosses the desktop bridge/backend error contract.

## Next

- Continue removing backend English/raw bridge details from config-page status surfaces.
