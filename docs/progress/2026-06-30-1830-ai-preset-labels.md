# AI Preset Labels Progress

Date: 2026-06-30 18:30

Linear: ongoing usability goal

## Done

- Updated the Config > Models preset map to show friendly AI model labels instead of raw aliases.
- Reused the existing route-label helper so `ds-flash`, `ds-pro`, and `sonnet` display consistently with the floating chat route labels.
- Kept the underlying SDK/CM_PARADEV preset ids and model aliases unchanged.

## Verification

- Red first: `rtk npm --prefix apps/desktop run test:unit -- --run src/configPage/ConfigPage.test.tsx -t "renders preset target models with friendly route labels"`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/configPage/ConfigPage.test.tsx -t "renders preset target models with friendly route labels"`
- `rtk npm --prefix apps/desktop run test:unit -- --run src/configPage/ConfigPage.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 47840`

## Risks Or Blockers

- The preset table is display-only; changing preset target aliases still belongs to the SDK/config contract.

## Next

- Address AI chat profile validation errors being hidden by frontend fallback profiles.
