# Assets Title Localization

## Summary

- Added the missing shared title-key mapping for the `assets` family.
- This lets Workspace, ModuleEditor, and BuildPage resolve the existing `modules.assets.title` locale key instead of falling back to raw SDK or English family labels.
- Added a focused mapper regression test so the assets family stays tied to the existing localized module title.

## Verification

- Red check: `rtk npm --prefix apps/desktop run test:unit -- src/projectModules.test.ts -t "assets family"` failed because `moduleTitleKeyForFamilyId("assets")` returned `undefined`.
- Green check: `rtk npm --prefix apps/desktop run test:unit -- src/projectModules.test.ts -t "assets family"`
- `rtk npm --prefix apps/desktop run test:unit -- src/projectModules.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- src/buildPage/buildPageModel.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk git diff --check`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri`

The PIHC3 Tauri smoke reached the Vite-ready state and launched `target/debug/paradev-desktop`; no delayed startup output appeared before stopping the process.
