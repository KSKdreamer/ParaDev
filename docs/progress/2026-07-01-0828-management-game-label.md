# Management Game Label

Date: 2026-07-01

## Summary

Localized known project game ids on the desktop Management page so true PIHC3 projects show a modder-facing game name instead of raw `hoi4`.

## Changes

- Added `management.game.hoi4` to English and Chinese desktop locale dictionaries.
- Rendered Management page game values through a small known-id label helper with unknown-id fallback.
- Added a PIHC3-shaped Chinese render test that rejects `<strong>hoi4</strong>`.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- --run src/projectManagement/ProjectManagementPage.test.tsx -t "localizes known project game ids"` failed before the implementation.
- `rtk npm --prefix apps/desktop run test:unit -- --run src/projectManagement/ProjectManagementPage.test.tsx src/i18n/locales.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk env PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 bash scripts/run.bash --tauri --port 47855` reached Vite ready, finished Cargo build, launched `target/debug/paradev-desktop`, and showed no late startup output before shutdown.
- `rtk git diff --check`
