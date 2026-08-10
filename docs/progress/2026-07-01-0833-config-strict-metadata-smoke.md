# Config Strict Metadata Smoke

Date: 2026-07-01

## Summary

Extended the rendered config-page smoke fixture to track the SDK-backed `paradev.build.strict_metadata` checkbox in addition to CLI output and build parallelism.

## Changes

- Added strict-metadata key and checked-state dataset fields to the config smoke state helper.
- Updated the config-page smoke fixture to detect `DESKTOP_CONFIG_KEYS.buildStrictMetadata`.
- Updated the smoke README with the strict-metadata toggle flow and expected dataset proof.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- --run e2e/config-page-smoke-state.test.ts` failed before the implementation on the missing dataset key.
- `rtk npm --prefix apps/desktop run test:unit -- --run e2e/config-page-smoke-state.test.ts src/configPage/ConfigPage.test.tsx src/App.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk env PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 bash scripts/run.bash --tauri --port 47856` reached Vite ready, finished Cargo build, launched `target/debug/paradev-desktop`, and showed no late startup output before shutdown.
- `rtk git diff --check`
