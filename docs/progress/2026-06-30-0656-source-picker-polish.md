# Source Picker Polish Progress

Date: 2026-06-30 06:56

Linear: active goal

## Done

- Audited the desktop config page against generated SDK config keys; no missing scalar config-page fields were found in the current source.
- Started a read-only localization explorer for remaining desktop hardcoded-English gaps.
- Tightened the module editor source picker layout so PIHC3 focus trees with long source file lists keep the selector readable beside the truncated source path.
- Added regression coverage for the compact PIHC3 source selector CSS and for the Chinese source-file accessible label in the focus source-picker branch.
- Smoked the native Tauri GUI with `projects/PIHC3`, opening real country and national focus modules with Chinese UI visible.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/ModuleEntityDetails.test.tsx src/styles/diagram.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri`

## Risks Or Blockers

- The native accessibility tree still reported a few stale English AX names for module editor containers even while the visible UI was Chinese and source/unit tests rendered those labels in Chinese. This needs a separate runtime isolation pass before treating it as a source bug.
- The Vite production build still reports the existing large chunk warning.

## Next

- Isolate the runtime AX-label mismatch in the Tauri WebKit tree, then continue with real PIHC3 workflow testing around focus/module editing.
