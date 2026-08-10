# 2026-06-20 14:03 - Diagram reparent append order

## Slice

Made canonical diagram reparenting append a moved node after the new parent's existing children.

## Changes

- Added a layout-model regression test for reparenting `moved-child` under a parent that already has `existing-child`.
- Updated `setDiagramTreeParent` so a reparented node preserves its current order unless the new parent already has children at or beyond that order; in that case it receives the next child order.
- Kept the existing visual-position preservation contract: auto/relative nodes still become relative to the new parent without moving on the canvas.

## Verification

- Red check: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/layoutModel.test.ts -t "appends a reparented node"` failed with `order: 0` instead of `order: 1`.
- Green check: the same focused command passed with `1 passed`.
- Targeted suite: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/layoutModel.test.ts` passed with `41 passed`.
- Regression check: `rtk npm --prefix apps/desktop run test:model` passed with `117 passed` after preserving old order when no append is required.

## Notes

- This keeps focus-tree parent edits deterministic when PIHC3 nodes are moved under a populated branch.
- The first implementation always lowered the moved node to the new parent's next order; `test:model` caught that as PIHC3 metadata YAML list churn, so the final rule only raises order when needed.
