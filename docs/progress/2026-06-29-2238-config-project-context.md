# Config Project Context

Time: 2026-06-29 22:38 CST

Continued the PIHC3 GUI usability loop by keeping active project context visible while browsing settings.

- Changed the desktop side panel so config mode reuses the same compact active-project selector as module mode.
- Updated the GUI spec so config side panels are explicitly project-aware.
- Added a ProjectPanel regression test proving config mode shows the active project name, path, selector label, and configuration list.
- Verified the real PIHC3 project can still be resolved through `desktop-state` with zero diagnostics.

Validation:

- Red first: `rtk npm --prefix apps/desktop run test:unit -- src/components/ProjectPanel.test.tsx` failed before the component change because config mode omitted the active project picker.
- Green focused: `rtk npm --prefix apps/desktop run test:unit -- src/components/ProjectPanel.test.tsx`: 6 passed.
- Adjacent UI: `rtk npm --prefix apps/desktop run test:unit -- src/components/ProjectPanel.test.tsx src/components/AppShell.test.tsx src/configPage/ConfigPage.test.tsx`: 44 passed.
- Desktop unit/build: `rtk npm --prefix apps/desktop run test:unit`: 645 passed; `rtk npm --prefix apps/desktop run build`: passed with the existing large-chunk warning.
- Config bridges: `rtk bash scripts/test.bash tests/test_desktop_api_selection.py tests/test_native_web_bridge.py tests/test_tauri_bridge.py -q -k "config"`: 22 passed.
- PIHC3 state probe: `rtk env PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 uv run paradev desktop-state --project /Users/magolor/Utils/ParaDev-3/projects/PIHC3 --no-browser --json` resolved active project `PIHC3`, source root `projects/PIHC3/src`, output root in the HoI4 mod folder, one registered project, and zero diagnostics.
- Native Tauri smoke: `rtk env PARADEV_ROOT=/tmp/paradev-config-project-context-smoke PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 bash scripts/run.bash --tauri --port 5223` compiled and launched `target/debug/paradev-desktop` without terminal startup errors before shutdown.
- `rtk bash scripts/flake.bash --ci`: passed.
- `rtk git diff --check`: passed.
- `rtk bash scripts/test.bash`: 1200 passed, 1 warning.

Risks:

- Native macOS accessibility inspection was not usable in this environment (`AXError.cannotComplete` / timeout), so rendered-native proof is limited to successful Tauri launch rather than an inspected screenshot.
- This slice only makes project context visible and switchable in config mode; it does not introduce project-scoped persisted config values.
- This slice did not change PIHC3 content.
