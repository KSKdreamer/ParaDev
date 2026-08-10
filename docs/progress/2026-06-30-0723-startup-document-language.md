# Startup Document Language Progress

Date: 2026-06-30 07:23

Linear: active goal

## Done

- Tightened the desktop startup shell metadata so the static `index.html` starts with `lang="zh-CN"`, matching the default GUI locale before React mounts.
- Added a regression test that ties the static startup document language to the shared `htmlLangForLocale("zh")` mapper.
- Kept the runtime locale application from the previous slice as the source of truth once React is mounted.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts` failed first on the old `lang="en"` shell, then passed after the HTML update.
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri`

## Risks Or Blockers

- The Vite production build still reports the existing large chunk warning.
- This is source-level startup verification; no fresh Computer Use AX snapshot was captured for this tiny metadata-only slice.

## Next

- Address the open-path target default drift between the Python desktop facade and GUI target picker on Linux and unknown platforms.
