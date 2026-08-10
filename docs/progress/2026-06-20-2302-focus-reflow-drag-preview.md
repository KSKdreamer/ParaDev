# 2026-06-20 23:02 - Focus Reflow Drag Preview

## Context

The focus tree editor already let users select `Reflow`, but drag preview still used a raw node offset model. That meant the final drop could auto-layout descendants differently from what the user saw while dragging.

## Changes

- Added a `diagramDragPreviewDocument` helper for pointer-drag projection.
- Kept existing smooth offset projection for normal node and branch drags.
- Switched `relayout-descendants` drag preview to use the canonical layout model through `moveDiagramNodeRelayoutDescendants`.
- Added regression coverage proving a reflow drag preview moves the selected branch and recalculates relative, auto, and pinned descendants into their preview auto-layout positions.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/ModuleEditor.test.tsx src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/layoutModel.test.ts src/styles/diagram.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts src/components/AppShell.test.tsx src/components/ProjectPanel.test.tsx src/components/Workspace.test.tsx src/moduleEditor/ModuleEditor.test.tsx src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/diagramImages.test.ts src/diagramEditor/diagramHistory.test.ts src/moduleEditor/diagramMetadata.test.ts src/styles/diagram.test.ts`
- `rtk npm --prefix apps/desktop run build`
- Browser QA at `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html?reflow-preview=4` with a 1440x900 viewport:
  - `Reflow` mode was visible and selected correctly.
  - Focus-tree grid and inspector remained usable.
  - Console check returned 0 warnings and 0 errors.

## Notes

The browser QA used DOM inspection and screenshot checks. The actual descendant reflow preview behavior is covered by unit tests because synthetic pointer events in the browser probe do not preserve native pointer capture semantics.
