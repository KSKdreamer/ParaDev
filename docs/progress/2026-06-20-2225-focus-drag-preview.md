# 2026-06-20 22:25 Focus Drag Preview

## Context

The focus-tree editor already had move modes for selected node, selected branch, node-only with fixed descendants, and node plus relaid-out descendants. The in-drag preview still moved only the selected focus tile, so branch movement looked wrong until pointer release. That contradicted the HOI4 focus-tree mental model where moving a focus branch should visibly carry the affected subtree.

## Changes

- Added `diagramDragPreviewNodeIds` to compute the nodes that should visually move for each drag mode.
- Updated pointer drag state to remember the active modifier command while dragging.
- Applied the drag offset to every preview-affected node:
  - normal node movement previews the selected node plus relative/auto descendants that will follow it;
  - subtree movement previews every descendant, including absolute descendants;
  - fixed-descendant and relayout-descendant movement preview only the selected node.
- Reused the existing child-index helper path so the preview stays deterministic on larger PIHC focus trees.

## Verification

- Red check:
  - `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
  - Failed before implementation because `diagramDragPreviewNodeIds` did not exist.
- Focused green:
  - `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
  - `1 passed / 107 tests`.
- Broader desktop slice:
  - `rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts src/components/AppShell.test.tsx src/components/ProjectPanel.test.tsx src/components/Workspace.test.tsx src/moduleEditor/ModuleEditor.test.tsx src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/diagramImages.test.ts src/diagramEditor/diagramHistory.test.ts src/moduleEditor/diagramMetadata.test.ts src/styles/diagram.test.ts`
  - `14 passed / 300 tests`.
- Build:
  - `rtk npm --prefix apps/desktop run build`
  - Passed with the existing large-chunk warning.
- Browser QA:
  - Opened `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html?drag-preview=1` at `1440 x 900`.
  - Confirmed the focus-tree grid, focus plaques, branch connectors, inspector, and minimap still render correctly in a normal desktop viewport.
  - Fresh console check returned zero warnings/errors.

## Follow-Up

- The next interaction slice should make connector previews follow dragged branch nodes, so the whole temporary focus-tree shape moves together before release.
- Larger PIHC focus trees still need more ergonomic branch selection and mode discovery around drag modifiers.
