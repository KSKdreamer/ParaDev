# Draft Apply REST Planning Progress

Date: 2026-06-29 16:13

Linear: TAL-000

## Done

- Routed native-web `applyProjectDraft` through generated `project.draft_apply` frontend API REST planning.
- Preserved the native Tauri `paradev_apply_project_draft` invoke path.
- Mapped GUI draft values to SDK-owned frontend API inputs, including `contentBase64` to REST `content_base64` for binary replacements.
- Added a regression test that rejects the legacy `/desktop/drafts/apply` shortcut.

## Verification

- `rtk npm --prefix apps/desktop test -- src/services/paradev.test.ts -t "applies project drafts through generated REST planning"` failed before the implementation and passed after it.
- `rtk npm --prefix apps/desktop test -- src/services/paradev.test.ts`
- `rtk npm --prefix apps/desktop run build`
- `rtk npm --prefix apps/desktop test`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk env PARADEV_PROJECTS=/Users/magolor/Utils/ParaDev-3/projects/PIHC3 bash scripts/run.bash --tauri --port 5215`
- Native screenshot: `/tmp/paradev-tauri-draft-apply-rest-plan.png`

## Risks Or Blockers

- The Tauri smoke proves the real PIHC3 native shell still launches; the changed route is exercised by the native-web service regression because native Tauri intentionally keeps direct invoke behavior.
- Build still reports the existing Vite chunk-size warning.

## Next

- Align `createModuleDraft` with generated `module.draft` REST planning by threading `projectId` into its service request.
