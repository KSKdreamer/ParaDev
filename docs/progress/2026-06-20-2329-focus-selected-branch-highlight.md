# 2026-06-20 23:29 - Focus Selected Branch Highlight

## Context

The focus tree editor is moving toward the HOI4 focus-tree model: focus icons laid out on a grid, connected by prerequisite/tree lines, with branches that can be moved or reflowed as coherent groups. The editor already had branch move modes and drag previews, but the selected branch was not visible until a drag started.

## Changes

- Added persistent `branch-member` classes for selected focus branch descendants.
- Added persistent `branch-member` classes for routed edges whose endpoints are both inside the selected branch.
- Added subtle canvas styling so branch membership is visible before drag without overpowering selected-node, search, or active preview states.
- Added regression coverage for node class generation, edge class generation, and static canvas rendering.

## Verification

- Red test first: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx` failed on the three new branch-highlight expectations.
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/layoutModel.test.ts src/diagramEditor/projectDiagram.test.ts src/moduleEditor/diagramSelection.test.ts src/moduleEditor/diagramMetadata.test.ts src/projectModules.test.ts src/moduleEditor/model.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- Browser QA at `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html` through the in-app browser:
  - Rendered 10 diagram nodes, 10 SVG edge paths, and 9 focus node images.
  - Selected `C08_REFORM` showed descendant branch nodes `C08_REFORM_ARMY` and `C08_REFORM_AIR`.
  - Selected branch tree edges `tree:C08_REFORM->C08_REFORM_ARMY` and `tree:C08_REFORM->C08_REFORM_AIR` were marked as `branch-member`.
  - Effective normal-window geometry had no page or body horizontal overflow.
  - Console entries contained only Vite and React development messages.

## Next

- Continue from this toward branch reflow controls that make affected descendants and recalculated descendant positions more explicit on the grid.
