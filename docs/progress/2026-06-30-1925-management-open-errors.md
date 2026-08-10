# Management Open Errors Progress

Date: 2026-06-30 19:25

Linear: continuous usability goal

## Done

- Stopped the project management path opener from swallowing desktop bridge failures.
- Reused the localized desktop bridge error mapping so failed path opens show the same modder-facing copy as the project panel and module editor.
- Rendered management path open failures as an inline `role="alert"` message in the expanded project details.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- --run src/projectManagement/ProjectManagementPage.test.tsx -t "management path open failures"` failed before the fix because the formatter did not exist and the source still swallowed `.catch(() => undefined)`.
- `rtk npm --prefix apps/desktop run test:unit -- --run src/projectManagement/ProjectManagementPage.test.tsx -t "management path open failures"`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/projectManagement/ProjectManagementPage.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 47840`

## Risks Or Blockers

- Existing Vite production build still reports the large chunk warning.
- Tauri smoke was stopped after launch with Ctrl-C, producing the expected code 130.

## Next

- Address scoped module browser load failures or AI profile load failures from the latest GUI reliability audit.
- Consider the PIHC3 flag metadata cleanup candidate: remove redundant `preview_source_path` from migrated flag asset component metadata.
