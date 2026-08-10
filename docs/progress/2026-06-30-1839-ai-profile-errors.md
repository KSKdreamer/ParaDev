# AI Profile Errors Progress

Date: 2026-06-30 18:39

Linear: continuous usability goal

## Done

- Stopped the desktop AI profile loader from swallowing Tauri/native backend failures.
- Kept the SDK-compatible AI chat profile fallback for no-backend rendering only.
- Added regression coverage so malformed `CM_PARADEV` AI chat profile overrides surface the backend validation error.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- --run src/services/paradev.test.ts -t "surfaces AI chat profile validation errors instead of falling back"` failed before the fix because the service resolved fallback profiles.
- `rtk npm --prefix apps/desktop run test:unit -- --run src/services/paradev.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 47840`

## Risks Or Blockers

- Existing Vite production build still reports the large chunk warning; this slice did not change bundle splitting.

## Next

- Continue API/CLI/GUI alignment checks around startup config reads and other desktop service fallbacks.
