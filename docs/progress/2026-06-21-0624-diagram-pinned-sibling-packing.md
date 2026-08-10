# Diagram Pinned Sibling Packing Progress

Date: 2026-06-21 06:24

Linear: TAL-000

## Done

- Updated the canonical diagram layout model so auto-positioned children shift away from absolute and relative siblings occupying the same child row.
- Added a regression test for HOI4-style focus rows where a pinned sibling and a relative sibling would otherwise collide with an auto child.
- Updated the existing HOI4 branch movement expectation where the new packing rule now moves an auto child to the next free grid slot instead of overlapping a relative sibling.

## Verification

- Red check first: `rtk bash -lc 'cd apps/desktop && npm run test:unit -- src/diagramEditor/layoutModel.test.ts'`
- `rtk bash -lc 'cd apps/desktop && npm run test:unit -- src/diagramEditor/layoutModel.test.ts'`
- `rtk bash -lc 'cd apps/desktop && npm run test:unit -- src/diagramEditor/layoutModel.test.ts src/diagramEditor/projectDiagram.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/styles/diagram.test.ts'`

## Risks Or Blockers

- The packing rule intentionally only reserves space for absolute and relative siblings. Existing auto sibling slot order and PIHC legacy auto-offset nudges remain unchanged.
- The editor still uses the custom SVG canvas rather than the React Flow renderer proposed in the design doc, but the canonical layout model is moving toward the same semantics.

## Next

- Browser-check the large PIHC3 focus/technology smoke pages after the next visual pass to verify the reduced row collisions in normal windows.
