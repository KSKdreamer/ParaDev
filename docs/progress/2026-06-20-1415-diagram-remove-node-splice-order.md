# 2026-06-20 14:15 - Diagram remove-node splice order

## Slice

Made canonical node-only deletion splice promoted children into the deleted node's order slot without colliding with later siblings or roots.

## Changes

- Tightened the existing child-promotion regression test so a later sibling shifts after two promoted children.
- Added a root-promotion regression test so promoted root children do not collide with an existing root.
- Updated `removeDiagramNodeOnly` to assign promoted children consecutive orders starting at the deleted node's order and shift later siblings/roots by the required offset.

## Verification

- Red check: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/layoutModel.test.ts -t "promoting children"` failed with later sibling/root nodes still at `order: 1`.
- Green check: the same focused command passed with `2 passed`.
- Targeted suite: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/layoutModel.test.ts` passed with `45 passed`.
- Model/metadata suite: `rtk npm --prefix apps/desktop run test:model` passed with `121 passed`.
- Diagram view suite: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx` passed with `86 passed`.
- Frontend build: `rtk npm --prefix apps/desktop run build` passed; Vite still reports the existing large-chunk warning.

## Notes

- This preserves the user's visual/tree intent for focus deletion: children replace the removed focus in-place, while PIHC3 metadata output avoids ambiguous sibling ordering.
