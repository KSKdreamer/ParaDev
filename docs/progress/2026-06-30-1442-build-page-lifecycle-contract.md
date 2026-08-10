# Build Page Lifecycle Contract Progress

Date: 2026-06-30 14:42

Linear: TAL-000

## Done

- Added frontend API operation metadata to the visible Build page start, status, and interrupt surfaces, including operation id, SDK call, REST method/path, payload, and confirmation requirement attributes.
- Kept the Build page runtime compact so the large generated frontend API helper remains lazy-loaded by the service layer.
- Added unit coverage that compares the compact Build lifecycle rows against `getFrontendApiActionDetail(...)` from the generated SDK contract, so binding drift fails without bloating the main GUI chunk.
- Preserved the compact translated action labels and existing ready-state copy behavior.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/buildPage/BuildPage.test.tsx src/data/frontendApi.test.ts src/data/frontendApiBindingIndex.test.ts src/services/paradev.test.ts`
- `rtk npm --prefix apps/desktop run build`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 4857`

## Risks Or Blockers

- The Build page now advertises the generated `build.*` lifecycle contract, but its primary buttons still use the existing dedicated handlers. A later slice should move visible execution state and write confirmation toward `getFrontendApiActionRunState(...)` without making the build dashboard feel like a generic API explorer.

## Next

- Add generated-action confirmation behavior for the mutating Build page actions while keeping the one-click modder workflow clear.
