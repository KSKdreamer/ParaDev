# Focus Source Slot Images Progress

Date: 2026-06-21 08:04

Linear: TAL-000

## Done

- Migrated source-backed focus layout display to PIHC2/HOI4DEV slot semantics: source `x/y` remain legacy left-edge coordinates, inferred `pw/subtreeWidth` determines the displayed icon column, and source `dx/dy/cx/cy/priority/dw/dc` continue to drive child packing.
- Added a source-focus slot layout mode for PIHC source-backed focus diagrams so auto children pack horizontally like HOI4 focus trees while ordinary diagrams keep the generic graph layout.
- Kept apply/review writeback in source semantics by converting displayed icon x back to raw source x for source-slot nodes.
- Preserved migrated PIHC3 focus preview images as the canvas image source and verified they render as actual hydrated PNGs at 34 px inside the 48 px grid.

## Verification

- Red: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/sourceBackedSmokeModel.test.ts` failed with C08 source root x rendered at raw source `9` instead of final icon column `12`.
- Green: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/sourceBackedSmokeModel.test.ts src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts src/moduleEditor/diagramMetadata.test.ts src/moduleEditor/sourceBackedDiagramApplySmokeModel.test.ts`.
- Broader desktop slice: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/sourceBackedSmokeModel.test.ts src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramImages.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/diagramMetadata.test.ts src/moduleEditor/sourceBackedDiagramApplySmokeModel.test.ts src/moduleEditor/ModuleEditor.test.tsx src/components/Workspace.test.tsx src/components/AppShell.test.tsx src/App.test.ts`.
- Build: `rtk npm --prefix apps/desktop run build` passed with the existing Vite chunk-size warning.
- Browser smoke at `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html`: 9 focus nodes, 9 data-backed PNG images, 0 placeholders, all images `34x34`, C08 plan row at SVG `y=144`, `TO_THE_WAR` at `translate(576 96)`, no horizontal body overflow, and no console warnings/errors.

## Risks Or Blockers

- Larger PIHC trees may still need more UI affordances for bulk branch reflow, but the source-backed C08 smoke path now uses the same horizontal slot math expected from the legacy focus compiler.

## Next

- Continue testing branch move/reflow controls against larger migrated focus trees, then fold the same source-slot parity into any remaining PIHC3 focus tree fixtures that expose legacy layout metadata.
