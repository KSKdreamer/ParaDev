# Management Source Roots Progress

Date: 2026-06-30 18:01

Linear: ongoing usability goal

## Done

- Updated Project Management to render every configured project source root instead of only the first one.
- Added indexed source labels for multi-root projects so PIHC3 import and overlay roots are distinguishable.
- Kept the existing single-source-root label unchanged for simpler projects.

## Verification

- Red first: `rtk npm --prefix apps/desktop run test:unit -- --run src/projectManagement/ProjectManagementPage.test.tsx -t "renders every configured source root"`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/projectManagement/ProjectManagementPage.test.tsx -t "renders every configured source root"`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/projectManagement/ProjectManagementPage.test.tsx src/i18n/locales.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 47840`

## Risks Or Blockers

- Source roots are displayed in SDK order; the GUI does not yet expose source-root editing from Project Management.

## Next

- Continue with stale post-write browser refresh behavior or REST inspection error normalization from the subagent findings.
