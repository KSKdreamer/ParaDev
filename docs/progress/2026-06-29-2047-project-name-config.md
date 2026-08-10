# Project Name Config Progress

## Summary

- Added `paradev.project.name` to the SDK-owned desktop config-value allowlist.
- Exposed the setting on the General config page as a "Config profile name" field, distinct from the active PIHC3/mod project title.
- Threaded the value through persisted desktop config reads, settings normalization, write planning, Tauri/native-web service tests, and localized English/Chinese UI copy.
- Updated the GUI spec so General-page SDK-backed command defaults include `paradev.project.name`.

## Verification

- Red checks first failed on missing `paradev.project.name` defaults, unsupported Python/REST config key, and missing React settings/UI shape.
- `rtk bash scripts/test.bash tests/test_desktop_api_selection.py tests/test_native_web_bridge.py -q`: 46 passed.
- `rtk npm --prefix apps/desktop run test:unit -- --run src/App.test.ts src/configPage/ConfigPage.test.tsx src/services/paradev.test.ts src/components/AppShell.test.tsx src/components/Workspace.moduleEditorConfig.test.tsx`: 95 passed.
- `rtk npm --prefix apps/desktop run build`: passed.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/desktop/local.py tests/test_desktop_api_selection.py tests/test_native_web_bridge.py`: passed.
- `rtk git diff --check -- <changed files>`: passed.
- Native GUI smoke: `PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 rtk bash scripts/run.bash --tauri --port 5195` compiled and launched `target/debug/paradev-desktop` with no terminal-side startup errors before manual stop.

## Notes

- Existing unrelated dirty work remains in `src/paradev/sdk/project.py`, `tests/test_pihc3_migration_contracts.py`, and the PIHC3 building-icon planning/source files. This slice does not stage or modify them.
- A read-only subagent identified `paradev.desktop.thumbnail_cache.max_kb` as a good next CM_PARADEV/config-page alignment slice.
