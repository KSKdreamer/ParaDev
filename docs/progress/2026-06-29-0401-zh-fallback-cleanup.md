# Chinese GUI Fallback Cleanup

Time: 2026-06-29 04:01 CST

Continued the GUI usability loop by removing English fallback text from common Chinese workbench surfaces that a modder reaches while browsing PIHC3.

- Added Chinese translations for Config Models labels, project status labels, workspace surface/status labels, status bar counters, and module editor accessibility/status labels.
- Extended Config, Workspace, StatusBar, ModuleEditor, ModuleEntityList, and ModuleEntityDetails unit coverage so these strings fail loudly if they regress to English fallback text.
- Render-validated the PIHC3 workspace through the native-web bridge after starting the Tauri desktop app with the PIHC3 project list.

Subagent notes:

- The module workbench translation audit found missing editor/list/source-tab labels; those are now covered in tests.
- The config coverage audit found no rendered Settings smoke fixture. A focused follow-up should add a Vite e2e fixture that opens Settings against PIHC3-like state and verifies visible config controls without overlapping the translation tests.

Validation:

- `PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 rtk bash scripts/run.bash --tauri`: compiled and started `target/debug/paradev-desktop` with no Tauri startup error; the desktop accessibility layer returned `AXError.cannotComplete`, so visual inspection used the native-web bridge.
- `PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 rtk bash scripts/run.bash --native-web --port 5182 --bridge-port 8767`: loaded the real PIHC3 project, verified Chinese Config Models labels, project status labels, empty workspace text, and module editor list/details/source-tab labels. Native-web produced expected native-progress warnings outside Tauri and one transient app-settings fetch warning; no translation/runtime crash occurred.
- `rtk npm --prefix apps/desktop run test:unit`: 43 files passed, 576 tests passed.
- `rtk npm --prefix apps/desktop run build`: passed; Vite reported the existing large-chunk warning.
- `git diff --check`: passed.
- `rtk bash scripts/flake.bash --ci`: passed.
- `rtk bash scripts/test.bash`: 1158 passed, 1 warning.

PIHC3 status: clean on `v3.1`; no PIHC3 files changed.
