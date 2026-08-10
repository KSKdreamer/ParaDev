# 2026-06-20 23:44 - Focus Move Mode Hints

## Context

The editor was already moving HOI4-style focus branches through Branch, Node, Node only, and Reflow modes, but the toolbar still made those modes hard to interpret. The screenshot feedback made the bigger product direction clear: this is a grid-like focus tree editor with connected focus icons, not a generic diagram editor. Users need to understand whether a nudge moves a whole branch, preserves relative descendants, keeps descendants fixed, or recalculates descendants.

## Changes

- Added a compact active move-mode behavior hint beside the affected-node count.
- Mapped each mode to user-facing semantics:
  - Branch: moves branch together.
  - Node: relative descendants follow.
  - Node only: keeps descendants in place.
  - Reflow: recalculates descendants.
- Added English and Chinese locale strings for the hints.
- Let the move-mode toolbar wrap cleanly in normal-width windows so the hint does not collide with controls.
- Updated the smoke harness to expose the Node only mode by wiring `onNodeMoveKeepingDescendants`.
- Added regression coverage for the hint formatter, rendered hint, toolbar wrap behavior, and hint truncation styling.

## Verification

- Red test first: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx` failed on the missing hint helper and rendered hint.
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/layoutModel.test.ts src/diagramEditor/projectDiagram.test.ts src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/diagramHistory.test.ts src/diagramEditor/diagramImages.test.ts src/moduleEditor/diagramMetadata.test.ts src/moduleEditor/diagramSelection.test.ts src/projectModules.test.ts src/moduleEditor/model.test.ts src/styles/diagram.test.ts src/components/Workspace.test.tsx src/moduleEditor/ModuleEditor.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- Browser QA at `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html` through the in-app browser:
  - Branch showed `Moves branch together` and `Affects 3 nodes`.
  - Node showed `Relative descendants follow` and `Affects 3 nodes`.
  - Node only showed `Keeps descendants in place` and `Affects 1 node`.
  - Reflow showed `Recalculates descendants` and `Affects 3 nodes`.
  - Rendered 10 nodes, 10 edge paths, and 9 focus images with no horizontal overflow.
  - Console warning/error count was 0.

## Next

- Continue moving the visual model toward full HOI4 focus-tree editing: grid snapping, focus icon surfaces, branch drag handles, and reflow previews that make relative placement updates visible before applying them.
