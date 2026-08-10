# 2026-06-20 22:06 HOI4 Focus Tree Grid Slice

## Context

The focus editor needed to move away from a generic flat module-card diagram and toward the Hearts of Iron IV national focus tree shape: square focus icons on a grid, connected prerequisite/tree lines, legacy PIHC positioning fields, and explicit branch movement policies.

Reference checked during this slice: `hoi4treesnap` describes rendering focus trees from game/mod focus graphics, focus icons, focus tree lines, fonts, and `nationalfocusview.gui` so screenshots resemble the in-game view. That matches the direction for the ParaDev editor: PIHC focus tree data should render as an icon-first focus grid, not as ordinary module rows.

## Changes

- Changed default embedded focus diagram nodes from `4 x 2` flat cards to `3 x 3` square icon tiles.
- Increased focus icon rendering from a small thumbnail cap to a 46px centered icon in the default 72px tile.
- Kept non-focus browser-item nodes on the existing rectangular layout.
- Added conditional SVG label compression for long focus labels so square tiles keep their grid footprint.
- Added a focus-specific layout regression for HOI4-style branch movement:
  - moving a branch preserves relative descendant offsets and moves the branch together;
  - moving a branch with descendant relayout converts descendants back to auto slots.
- Updated metadata persistence golden expectations for the taller focus tile grid.
- Expanded the diagram apply-review smoke page from a two-node placeholder into a compact PIHC3/HOI4-style focus tree with 10 focus nodes, 17 links, relative branches, auto-laid descendants, one missing-icon placeholder, and real move handlers wired to the layout model.
- Updated the e2e fixture README to describe the focus-grid smoke coverage.

## Verification

- Red check before implementation:
  - `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/projectDiagram.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/layoutModel.test.ts`
  - Failed on the expected focus tile size and icon geometry assertions.
- Focused green:
  - `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/projectDiagram.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/layoutModel.test.ts`
  - `3 passed / 176 tests`.
- Focused post-label green:
  - `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts src/moduleEditor/diagramMetadata.test.ts`
  - `4 passed / 229 tests`.
- Broader desktop slice:
  - `rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts src/components/AppShell.test.tsx src/components/ProjectPanel.test.tsx src/components/Workspace.test.tsx src/moduleEditor/ModuleEditor.test.tsx src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/diagramImages.test.ts src/diagramEditor/diagramHistory.test.ts src/moduleEditor/diagramMetadata.test.ts src/styles/diagram.test.ts`
  - `14 passed / 297 tests`.
- Build:
  - `rtk npm --prefix apps/desktop run build`
  - Passed with the existing large-chunk warning.
- Browser QA:
  - Opened `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html?hoi4-grid=2` at `1440 x 900`.
  - Inspected the viewport screenshot: focus nodes render as square icon tiles on a connected grid; inspector and toolbar stay outside the canvas; missing local image renders as an icon slot placeholder.
  - Console warning/error check returned zero warnings/errors for the fresh smoke page.

## Follow-Up

- The next focus-tree fidelity slice should improve the actual visual language beyond this structural fix: HOI4-like focus frames/plaques, better route-line styling, and denser tree fitting for large PIHC trees.
- The current layout model already supports `relative_position_id`, `dx/dy`, `cx/cy`, `w`, `dw/dc`, and `priority`; future work should preserve that model and expose clearer UI affordances for choosing subtree move versus descendant relayout.
