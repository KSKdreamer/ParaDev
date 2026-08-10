# Source Text REST Planning Progress

Date: 2026-06-29 16:03

Linear: TAL-000

## Done

- Routed the native-web source text reader through generated `project.source_text` frontend API REST planning.
- Kept the Tauri `paradev_read_text_source` invoke path unchanged.
- Threaded `browser.project_id` into module editor source loading and diagram metadata draft text loading.
- Updated the service regression test to reject the legacy `/desktop/sources/text` shortcut.

## Verification

- `rtk npm --prefix apps/desktop test -- src/services/paradev.test.ts -t "loads project browser and source text"` failed before the implementation and passed after it.
- `rtk npm --prefix apps/desktop test -- src/services/paradev.test.ts`
- `rtk npm --prefix apps/desktop test -- src/moduleEditor/ModuleEntityDetails.test.tsx`
- `rtk npm --prefix apps/desktop test -- src/moduleEditor/ModuleEditor.test.tsx src/moduleEditor/ModuleEditor.gameRoot.test.tsx`
- `rtk npm --prefix apps/desktop run build`
- `rtk npm --prefix apps/desktop test`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 bash scripts/run.bash --tauri --port 5214`
- Native screenshot: `/tmp/paradev-tauri-source-text-rest-plan.png`

## Risks Or Blockers

- A read-only subagent review was started but did not return before shutdown.
- Tauri smoke confirmed the real native PIHC3 window renders; the changed route itself is exercised by the native-web service regression because Tauri source reads intentionally use the direct invoke path.

## Next

- Continue aligning remaining native-web draft routes with generated frontend API REST planning.
