# Build Config Errors Progress

Date: 2026-06-30 19:08

Linear: continuous usability goal

## Done

- Stopped BuildPage from swallowing SDK-backed config read and write failures.
- Added config-specific build error messages so failures say build settings could not be loaded or saved instead of looking like build command failures.
- Added English and Chinese translations for BuildPage config load/save failures.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- --run src/buildPage/BuildPage.test.tsx -t "formats bridge errors"` failed before the fix because config-read errors fell through to `Build failed`.
- `rtk npm --prefix apps/desktop run test:unit -- --run src/buildPage/BuildPage.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 47840`

## Risks Or Blockers

- Existing Vite production build still reports the large chunk warning.

## Next

- Continue tightening config and AI/chat UX around visible backend failures, then return to PIHC3 minimization work.
