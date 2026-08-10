# Native-Web AI Profile Smoke Progress

Date: 2026-06-30 11:23 CST
Linear: active usability goal

## Done

- Added a red-first regression for native-web bridge mode so boot progress syncing no longer calls Tauri `getCurrentWindow()` when only the REST bridge is present.
- Narrowed native progress syncing to the real Tauri runtime while keeping native-web bridge support for SDK/desktop API operations.
- Ran a rendered native-web PIHC3 smoke under an isolated `PARADEV_ROOT`, toggled the `说明 HOI4 代码` AI profile's `模板` source, saved through the row-local profile control, reloaded the GUI, verified persistence through the Python SDK facade, then reset the profile.
- Documented the repeatable bridge-backed PIHC3 smoke in `apps/desktop/e2e/README.md`.

## Verification

- Red first: `rtk npm --prefix apps/desktop run test:unit -- src/services/nativeProgress.test.ts` failed because `syncNativeBootProgress()` requested `getCurrentWindow()` in native-web bridge mode.
- Focused unit test after fix: `rtk npm --prefix apps/desktop run test:unit -- src/services/nativeProgress.test.ts` passed, 7 tests.
- Rendered native-web PIHC3 smoke: `rtk env PARADEV_ROOT=/var/folders/w4/3wzq3qvn7b9804gx62f18k280000gn/T/paradev-native-web-smoke.XXXXXXXX.V2GJXcRWyf PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --native-web --port 5208 --bridge-port 8768`.
- GUI smoke result: localized Config -> Models opened on `The Pony In The High Castle`; `DeepSeek` was visible; `说明 HOI4 代码` changed from `项目 / 选区` to `项目 / 选区 / 模板` after row-local save, survived a fresh page load, and reset back to `项目 / 选区`.
- Python SDK facade during smoke returned `{"defaultRole": "chat", "projectRoot": "projects/PIHC3", "sourceKinds": ["project", "selection", "templates"]}` after save and `["project", "selection"]` after reset.
- Browser console check after smoke: zero warnings and zero errors; the dev server did not log `Failed to sync native ParaDev progress`.
- Desktop unit suite: `rtk npm --prefix apps/desktop run test:unit` passed, 714 tests.
- Desktop production build: `rtk npm --prefix apps/desktop run build` passed with the existing Vite large-chunk warning.
- Flake gate: `rtk bash scripts/flake.bash --ci` passed.
- Fast repo gate: `rtk bash scripts/test.bash` passed, 1228 tests with 1 warning.

## Risks Or Blockers

- This smoke uses `--native-web` to exercise the real REST bridge and rendered GUI, not the packaged Tauri window.
- The first manual DOM attempt clicked the first disabled page-level `保存` button; the documented smoke now explicitly uses the row-local `说明 HOI4 代码` save button.

## Next

- Decide whether AI profile overrides are global or project-scoped; the current API accepts `project_root`, and a read-only subagent audit found that storage still appears global.
- Convert the bridge-backed AI profile persistence smoke into an automated rendered test once the native-web bridge harness can be started/stopped reliably from CI.
- Continue closing GUI usability gaps with PIHC3 as the default manual smoke project.
