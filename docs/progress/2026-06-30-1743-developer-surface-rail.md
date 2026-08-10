# Developer Surface Rail Progress

Date: 2026-06-30 17:43

Linear: ongoing usability goal

## Done

- Replaced the Developer rail placeholder with the existing surface-contract table.
- Routed Developer through a pinned synthetic `surface` workspace tab so API/CLI/GUI surfaces are reachable from the rail.
- Split the surface table into a shared Workspace helper and kept surface tabs free of module-focused status copy.

## Verification

- Red first: `rtk npm --prefix apps/desktop run test:unit -- --run src/components/AppShell.test.tsx -t "developer rail as surface contracts"`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/components/AppShell.test.tsx -t "developer rail as surface contracts"`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/components/AppShell.test.tsx src/components/Workspace.test.tsx src/i18n/locales.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 47840`

## Risks Or Blockers

- The Developer rail currently presents the first seven surface rows, matching the existing surface table limit.

## Next

- Continue PIHC3-first GUI testing for remaining placeholder or raw internal labels.
