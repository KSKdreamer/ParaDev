# Explicit Refresh Cache Progress

Date: 2026-06-30 18:20

Linear: ongoing usability goal

## Done

- Added a refresh policy helper so automatic startup refreshes can use the project-browser cache.
- Changed explicit project refreshes with a project root to bypass cached browser payloads and fetch fresh SDK browser data.
- Preserved existing scoped-browser behavior so summary-only payloads still allow family/module scoped loads.

## Verification

- Red first: `rtk npm --prefix apps/desktop run test:unit -- --run src/App.test.ts -t "uses project browser cache only for automatic startup refreshes"`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/App.test.ts -t "uses project browser cache only for automatic startup refreshes"`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/App.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 47840`

## Risks Or Blockers

- Project switches with an explicit root also bypass cache, trading startup speed for fresher SDK-backed state.

## Next

- Continue PIHC3-first GUI testing for remaining cache, refresh, or post-write stale-state cases.
