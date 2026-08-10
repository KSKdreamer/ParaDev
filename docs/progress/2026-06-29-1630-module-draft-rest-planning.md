# Module Draft REST Planning Progress

Date: 2026-06-29 16:30

Linear: TAL-000

## Done

- Routed native-web `createModuleDraft` through generated `module.draft` frontend API REST planning.
- Threaded `browser.project_id` into module create preview and scaffold apply calls.
- Kept the native Tauri `paradev_create_module_draft` invoke path unchanged.
- Added a regression test that rejects the legacy `/desktop/modules/draft` shortcut.

## Verification

- `rtk npm --prefix apps/desktop test -- src/services/paradev.test.ts -t "creates module drafts through generated REST planning"` failed before the implementation and passed after it.
- `rtk npm --prefix apps/desktop test -- src/services/paradev.test.ts`
- `rtk npm --prefix apps/desktop test -- src/moduleEditor/ModuleEditor.test.tsx src/moduleEditor/ModuleEditor.gameRoot.test.tsx`
- `rtk npm --prefix apps/desktop run build`
- `rtk npm --prefix apps/desktop test`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 bash scripts/run.bash --tauri --port 5216`
- Native screenshot: `/tmp/paradev-tauri-module-draft-rest-plan.png`

## Risks Or Blockers

- The Tauri smoke proves the real PIHC3 native shell still launches; the changed route is exercised by the native-web service regression because native Tauri intentionally keeps direct invoke behavior.
- Build still reports the existing Vite chunk-size warning.

## Next

- Audit remaining runtime-only desktop routes and prioritize the next user-facing SDK/GUI alignment slice.
