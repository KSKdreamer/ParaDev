# LLM Route Status I18n Progress

Date: 2026-06-29 18:55

Linear: N/A

## Done

- Stopped rendering raw backend `testDetail` strings directly in the config Models page.
- Added localized LLM route-test summaries for ready, empty-response, warning, and error states.
- Preserved the SDK/desktop bridge payload evidence in `testDetail`; the change is React display-only.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- --run src/configPage/ConfigPage.test.tsx src/i18n/locales.test.ts`
- `rtk git diff --check`
- `rtk npm --prefix apps/desktop run build`
- `PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 rtk bash scripts/run.bash --tauri --port 5202`

## Risks Or Blockers

- The UI still infers empty-response warnings from the raw detail text. A future SDK/bridge hardening slice should add a structured route-test result code while keeping raw detail as diagnostics evidence.

## Next

- Add structured LLM route-test result codes in the Python SDK and TypeScript bridge, then have React use the code instead of detail substring matching.
