# Source Layout Hint Smoke Progress

Date: 2026-06-21 08:17

Linear: TAL-000

## Done

- Wired the source-backed `C08_PARTIV` diagram smoke to the real selected-node PIHC layout hint form.
- Exposed selected layout hints as `priority`, `w`, `dw`, and `dc` datasets so rendered smoke checks can prove the source-layout edit path.
- Added model coverage showing a `FOCUS_C08_TO_THE_WAR` hint edit reflows its child focus plan row while leaving the independent root branch fixed.
- Updated the e2e smoke README with the rendered inspector flow for editing priority, lane width, lane delta, and center offset.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/sourceBackedSmokeModel.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/projectDiagram.test.ts src/moduleEditor/diagramMetadata.test.ts src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/sourceBackedSmokeModel.test.ts src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramImages.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/diagramMetadata.test.ts src/moduleEditor/sourceBackedDiagramApplySmokeModel.test.ts src/moduleEditor/ModuleEditor.test.tsx src/components/Workspace.test.tsx src/components/AppShell.test.tsx src/App.test.ts`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke at `http://127.0.0.1:5180/e2e/diagram-source-backed-smoke.html`: submitted the inspector form for `FOCUS_C08_TO_THE_WAR` with priority `15`, lane `8`, lane delta `2`, and center `1`; the page reported `priority=15|w=8|dw=2|dc=1`, reflowed plan children to `8,3`, `11,3`, and `14,3`, kept nine actual `34x34` focus images, and reported no console warnings or errors.
