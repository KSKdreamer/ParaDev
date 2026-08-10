# 2026-06-21 00:00 - Focus Drag Coordinate Preview

## Context

Selected focus nodes now show grid and relative coordinate badges on the canvas. The remaining mismatch was live movement: for non-reflow drags, the focus tile can move under the pointer while the badge was still derived from the original resolved node. A HOI4-style focus tree editor needs the placement readout to reflect the snapped grid result users are about to commit.

## Changes

- Added `diagramPreviewFocusCoordinateBadgeNode(...)` to project selected-focus badges from a snapped drag delta.
- For relative focuses, the preview updates both resolved `x/y` and stored `dx/dy`.
- For pinned or auto focuses, the preview updates resolved `x/y` without inventing a relative offset.
- Wired non-reflow drag preview deltas into the selected focus badge path.
- Left reflow previews on the existing preview-document path, since those nodes are already resolved through the moved/relaid-out document.

## Verification

- Red test first: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx` failed on the missing preview helper.
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/layoutModel.test.ts src/diagramEditor/projectDiagram.test.ts src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/diagramHistory.test.ts src/diagramEditor/diagramImages.test.ts src/moduleEditor/diagramMetadata.test.ts src/moduleEditor/diagramSelection.test.ts src/projectModules.test.ts src/moduleEditor/model.test.ts src/styles/diagram.test.ts src/components/Workspace.test.tsx src/moduleEditor/ModuleEditor.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- Browser QA at `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html` through the in-app browser:
  - Pointer drag automation delivered a drag-start but not movement events, so the live pointer preview was covered by the unit-level snapped-delta test.
  - Keyboard grid movement updated selected `C08_REFORM` from `x 5 y 5 / dx -5 dy +5` to `x 6 y 5 / dx -4 dy +5`.
  - Inspector text updated to `Grid 6, 5` and `Offset -4, 5 from C08_PARTIV`.
  - Rendered 10 nodes, 10 edge paths, and 10 focus image or placeholder elements.
  - Normal-window geometry had no horizontal overflow.
  - Console warning/error count was 0.

## Next

- Continue toward direct-manipulation polish: a visible drag ghost/anchor line, branch drag handles, and clearer before/after descendant reflow previews.
