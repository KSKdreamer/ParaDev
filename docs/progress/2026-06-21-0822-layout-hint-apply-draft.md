# Layout Hint Apply Draft Progress

Date: 2026-06-21 08:22

Linear: TAL-000

## Done

- Added a source-backed PIHC3 apply fixture for editing `FOCUS_C08_TO_THE_WAR` layout hints.
- Verified the source-info draft plan writes only `legacy/C08_TO_THE_WAR/info.json` and includes `priority`, `w`, `dw`, and `dc`.
- Updated the rendered apply-review smoke to recompute the real diagram metadata draft plan from the current canvas document and expose the planned source edit path/text.
- Documented the browser smoke path from inspector layout hint edit to review-gated Apply.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/sourceBackedDiagramApplySmokeModel.test.ts src/moduleEditor/diagramMetadata.test.ts src/moduleEditor/ModuleEditor.test.tsx src/diagramEditor/sourceBackedSmokeModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/sourceBackedSmokeModel.test.ts src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramImages.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/diagramMetadata.test.ts src/moduleEditor/sourceBackedDiagramApplySmokeModel.test.ts src/moduleEditor/ModuleEditor.test.tsx src/components/Workspace.test.tsx src/components/AppShell.test.tsx src/App.test.ts`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke at `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html`: edited the selected focus layout hints to priority `15`, lane `8`, lane delta `2`, and center `1`; the page reported one source edit for `legacy/C08_TO_THE_WAR/info.json`, `data-paradev-diagram-apply-layout-hint-draft="1"`, source text containing `"w": 8`, `"dw": 2`, and `"dc": 1`, then review/apply completed with `data-paradev-diagram-apply-count="1"` and no console warnings or errors.
