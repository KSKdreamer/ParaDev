# Focus Compact Auto Rows Progress

Date: 2026-06-21 07:45

Linear: TAL-000

## Done

- Added document-level diagram layout options and set focus diagrams to `layerGap: 0`, so auto-positioned PIHC/HOI4 focus children render on the next grid row instead of the generic graph gap.
- Preserved legacy `dx/dy/cx/cy` offset writeback while making the canvas display compact HOI4-style rows for source-backed C08 focus trees.
- Kept diagram JSON import/export aware of layout options so saved diagram drafts retain compact focus spacing.

## Verification

- Red: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/sourceBackedSmokeModel.test.ts` failed with `FOCUS_C08_PLAN_TWILIGHT.worldY` at `7` instead of `3`.
- Green: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/sourceBackedSmokeModel.test.ts src/diagramEditor/projectDiagram.test.ts src/diagramEditor/diagramJson.test.ts src/diagramEditor/layoutModel.test.ts`.
- Broader desktop slice: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/sourceBackedSmokeModel.test.ts src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramImages.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/diagramMetadata.test.ts src/moduleEditor/sourceBackedDiagramApplySmokeModel.test.ts src/moduleEditor/ModuleEditor.test.tsx src/components/Workspace.test.tsx src/components/AppShell.test.tsx src/App.test.ts`.
- Build: `rtk npm --prefix apps/desktop run build` passed with the existing Vite chunk-size warning.
- Browser smoke at `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html`: 9 focus nodes, 9 data-backed PNG images, 0 placeholders, 34 px images inside 48 px slots, `TO_THE_WAR` at SVG `y=96`, C08 plan nodes at `y=144`, no horizontal body overflow, and no console warnings/errors.

## Risks Or Blockers

- The GUI still approximates HOI4DEV horizontal subtree packing; a later slice should align `pw/w/dw/dc` left-edge semantics more exactly with PIHC2 if users need pixel-level parity.

## Next

- Continue tightening source-backed focus movement/reflow behavior against larger PIHC3 trees and legacy PIHC2 positioning fixtures.
