# 2026-06-20 23:36 - Focus Active Move Footprint

## Context

The focus tree editor now shows the selected branch before drag. The next usability gap was that structural branch membership and the active move mode footprint were the same visual concept, even though Branch, Node, Node only, and Reflow affect different sets of nodes depending on relative, auto, and pinned descendants.

## Changes

- Added `move-affected` classes for nodes affected by the currently active selected-node move mode.
- Added `move-affected` classes for edges whose endpoints are both in that active move footprint.
- Added minimap `move-affected` classes so the affected branch remains visible in normal window layouts.
- Kept `branch-member` as the structural selected-branch marker and made `move-affected` the stronger active-mode marker.
- Added regression coverage for node class generation, edge class generation, minimap class generation, and rendered canvas output.

## Verification

- Red test first: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx` failed on the new `move-affected` expectations.
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/layoutModel.test.ts src/diagramEditor/projectDiagram.test.ts src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/diagramHistory.test.ts src/diagramEditor/diagramImages.test.ts src/moduleEditor/diagramMetadata.test.ts src/moduleEditor/diagramSelection.test.ts src/projectModules.test.ts src/moduleEditor/model.test.ts src/styles/diagram.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- Browser QA at `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html` through the in-app browser:
  - Rendered 10 diagram nodes, 10 SVG edge paths, and 9 focus node images.
  - Branch, Node, and Reflow modes all marked the selected `C08_REFORM` branch footprint for this smoke data: `C08_REFORM`, `C08_REFORM_ARMY`, and `C08_REFORM_AIR`.
  - Active footprint tree edges were `tree:C08_REFORM->C08_REFORM_ARMY` and `tree:C08_REFORM->C08_REFORM_AIR`.
  - The minimap marked the same active footprint nodes.
  - Normal-window smoke geometry had no horizontal overflow.
  - Console warning/error count was 0.

## Next

- Continue toward clearer mode copy or controls for the distinction between moving a node with relative descendants and moving the node while preserving descendant world positions.
