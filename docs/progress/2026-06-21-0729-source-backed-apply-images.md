# Source Backed Apply Images Progress

Date: 2026-06-21 07:29 CST

Linear: TAL-000

## Done

- Kept diagram image hydration source paths project-relative, so migrated `src/modules/focus_asset_component/.../preview.png` paths reach the Tauri `paradev_read_binary_source` bridge directly instead of being pre-expanded in React.
- Reworked `diagram-apply-review-smoke.html` to use the shared source-backed PIHC3 `C08_PARTIV` diagram document and mocked binary-source bridge instead of a duplicated direct-import fixture.
- Updated the e2e fixture docs to document the source-backed focus image path, bridge read count, and 48 px grid / 34 px image-size expectation.

## Verification

- Red first: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramImages.test.ts` failed because the loader still sent `/workspace/projects/PIHC3/src/.../icon.png` instead of `src/.../icon.png`.
- Green: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramImages.test.ts`.
- Targeted GUI/model suite: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramImages.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/sourceBackedSmokeModel.test.ts src/moduleEditor/sourceBackedDiagramApplySmokeModel.test.ts src/components/Workspace.test.tsx src/components/AppShell.test.tsx src/App.test.ts`.
- Build: `rtk npm --prefix apps/desktop run build` passed with the existing large-chunk warning.
- Browser smoke at `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html`: 9 focus images, 0 placeholders, `Images 9/9`, 9 binary reads, 9 cache writes, last source path `src/modules/focus_asset_component/FOCUS_ASSET_COMPONENT_FOCUS_C08_PLAN_TWILIGHT/preview.png`, SVG image size `34`, grid `48`, no horizontal body overflow.

## Risks Or Blockers

- This keeps the GUI on the current SVG renderer. React Flow migration remains a broader editor-architecture task.
