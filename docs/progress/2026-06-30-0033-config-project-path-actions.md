# Config Project Path Actions Progress

Date: 2026-06-30 00:33

Linear: continuous usability goal

## Done

- Added compact open actions to the Config > Projects path rows for project root, source roots, output folder, build cache, and configured HOI4 game root.
- Routed those actions through the existing desktop `openProjectPath(...)` service, which delegates to the Tauri/native-web Python desktop open-path bridge.
- Reused the Build page output-path fallback so Config and Build open the same generated mod folder when `outputRoot` is unset.
- Added English and Chinese labels for the path actions and updated the GUI spec.
- Ran two read-only subagent audits for path UX and SDK/bridge alignment.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/configPage/ConfigPage.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/components/Workspace.moduleEditorConfig.test.tsx src/components/Workspace.test.tsx src/components/AppShell.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk bash scripts/flake.bash --ci`
- `rtk git diff --check`
- `rtk env PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 bash scripts/run.bash --tauri`

## Risks Or Blockers

- The UI still only opens configured paths; folder picking, existence probes, and Finder/Explorer reveal-select behavior need separate SDK/bridge contracts.

## Next

- Add path validation and browse/select-folder flows through Python desktop APIs.
