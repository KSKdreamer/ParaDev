# Config Backend Required Progress

Date: 2026-06-30 18:58

Linear: continuous usability goal

## Done

- Made SDK-backed desktop config reads and writes reject when neither Tauri nor the native-web bridge is available.
- Added regression coverage so browser-only/no-bridge mode cannot pretend a `CM_PARADEV` config value was read or saved.
- Added localized English and Chinese bridge errors for config read/write backend requirements.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- --run src/services/paradev.test.ts -t "rejects SDK-backed config values outside the desktop backend"` failed before the fix because `readConfigValue` resolved `undefined`.
- `rtk npm --prefix apps/desktop run test:unit -- --run src/services/paradev.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 47840`

## Risks Or Blockers

- Existing Vite production build still reports the large chunk warning.
- Follow-up: BuildPage still has local catch-and-ignore paths for config reads/writes.

## Next

- Add BuildPage error-state coverage so build-specific config read/write failures are visible instead of silently using optimistic local state.
