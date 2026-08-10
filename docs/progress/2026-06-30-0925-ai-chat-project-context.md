# AI Chat Project Context Progress

Date: 2026-06-30 09:25 CST
Linear: active usability goal

## Done

- Added project-level AI chat context for config and empty workspace views, so the default Project role has useful context before a module tab is selected.
- Kept templates and diagnostics attached after the project context for non-module workspaces.
- Localized the project summary in English and Chinese.
- Fixed review findings before commit: project metadata sources no longer carry a root `path`, and summary-browser row counts use SDK family totals instead of `items.length`.

## Verification

- Red first: `rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts -t "keeps project AI chat context available from empty or config workspaces"` failed because non-module workspaces only attached templates.
- Red first after review: `rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts -t "project AI chat context"` failed because the project source still included `path` and summary-browser rows reported `0`.
- Focused green: `rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts -t "project AI chat context"` passed, 2 tests.
- Focused green: `rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts -t "localizes project-level AI chat context"` passed, 1 test.
- App tests: `rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts` passed, 44 tests.
- Desktop unit suite: `rtk npm --prefix apps/desktop run test:unit` passed, 705 tests.
- Desktop production build: `rtk npm --prefix apps/desktop run build` passed.
- Fast repo gate: `rtk bash scripts/test.bash` passed, 1227 tests.
- Diff hygiene: `rtk git diff --check` passed.
- Native PIHC3 smoke: `rtk env PARADEV_PROJECTS=projects/PIHC3 bash scripts/run.bash --tauri --port 5200` launched the Tauri dev app and was manually stopped after stable startup.

## Risks Or Blockers

- The desktop build still reports the existing Vite large-chunk warning.
- The Tauri smoke was startup-level only; deeper rendered interaction checks remain needed.

## Next

- Continue visual and workflow testing in the native PIHC3 app, especially using the floating chat from config and module views.
- Expand the AI role/source editor once the cross-page project context path stays stable.
