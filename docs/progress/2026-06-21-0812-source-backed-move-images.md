# Source Backed Move Images Progress

Date: 2026-06-21 08:12

Linear: TAL-000

## Done

- Extended the PIHC3 `C08_PARTIV` source-backed diagram smoke with direct controls for Reset, Move Subtree, Move Node Only, and Relayout Descendants.
- Added model coverage proving the HOI4-style movement contract: subtree moves preserve child offsets, node-only moves pin descendants visually, and relayout-descendants repacks children as auto nodes under the moved parent.
- Updated the source-backed smoke documentation with dataset checks for migrated preview image hydration, 34 x 34 px icons inside 48 px focus slots, and each movement mode.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/sourceBackedSmokeModel.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/projectDiagram.test.ts src/moduleEditor/diagramMetadata.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/sourceBackedSmokeModel.test.ts src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramImages.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/diagramMetadata.test.ts src/moduleEditor/sourceBackedDiagramApplySmokeModel.test.ts src/moduleEditor/ModuleEditor.test.tsx src/components/Workspace.test.tsx src/components/AppShell.test.tsx src/App.test.ts`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke at `http://127.0.0.1:5180/e2e/diagram-source-backed-smoke.html`: nine actual `.project-diagram-node-image.focus-icon` SVG images, zero focus placeholders, all images `34x34`, base/subtree/node-only/relayout movement datasets matched the expected deltas, and no console warnings or errors were reported.
