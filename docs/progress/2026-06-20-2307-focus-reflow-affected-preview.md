# 2026-06-20 23:07 - Focus Reflow Affected Preview

## Context

The focus tree editor reflow drag preview now projects the canonical relayout result, but only the selected node was marked as the active preview node. In practice that hid which descendant nodes were part of the pending reflow operation.

## Changes

- Updated `diagramDragPreviewNodeIds` so `relayout-descendants` includes the full affected focus subtree, matching branch drag visibility.
- Kept fixed-descendant movement scoped to the selected node only.
- Changed canvas node rendering so all preview node ids receive the dragging/preview state, including reflow previews that are backed by a projected document instead of a raw pixel offset.
- Added regression coverage proving reflow preview affected ids include selected, relative, auto-layout, and pinned descendants.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/ModuleEditor.test.tsx src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/layoutModel.test.ts src/styles/diagram.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts src/components/AppShell.test.tsx src/components/ProjectPanel.test.tsx src/components/Workspace.test.tsx src/moduleEditor/ModuleEditor.test.tsx src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/diagramImages.test.ts src/diagramEditor/diagramHistory.test.ts src/moduleEditor/diagramMetadata.test.ts src/styles/diagram.test.ts`
- `rtk npm --prefix apps/desktop run build`
- Browser QA at `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html` through the in-app browser:
  - Smoke page rendered 10 focus nodes, 10 routed edges, and 9 focus node images.
  - `Reflow` move mode was visible, enabled, and became the pressed mode when clicked.
  - Recent console logs contained only Vite and React development messages, with no warning or error entries.

## Notes

This slice verifies the browser surface is healthy and the mode is selectable. The exact reflow affected-node set is covered by unit tests because pointer-drag visual sampling is still fragile in the browser bridge.
