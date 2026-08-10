# Build Bridge Error Localization Progress

Date: 2026-06-30 06:20

Linear: active goal

## Done

- Added a shared desktop bridge error mapper for build-page Tauri fallback messages.
- Localized build-page open-output and HOI4-launch bridge errors so Chinese action alerts no longer mix raw English bridge text into the message.
- Kept non-bridge runtime details, such as Steam failures, unchanged for debugging value.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/buildPage/BuildPage.test.tsx -t "formats bridge errors"`
- `rtk npm --prefix apps/desktop run test:unit -- src/buildPage/BuildPage.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`

## Risks Or Blockers

- The mapper is currently wired into the build page only; adjacent config, module editor, and AI surfaces may still wrap raw desktop bridge errors.
- The Vite production build still reports the existing large chunk warning.

## Next

- Apply the same bridge-error mapping to the next highest-impact mixed-language GUI error path, starting with project open/source open failures in `App.tsx` and `ModuleEntityDetails.tsx`.
