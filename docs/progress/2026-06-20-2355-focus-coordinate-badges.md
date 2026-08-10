# 2026-06-20 23:55 - Focus Coordinate Badges

## Context

The focus-tree inspector already exposes resolved grid position, stored relative offsets, and PIHC layout hints. The remaining usability gap was that the canvas itself did not show those coordinates where users look while moving HOI4-style focus icons. This made branch drag and relative-position editing feel less like a focus-tree editor and more like a generic graph.

## Changes

- Added selected-focus coordinate badges directly on the SVG canvas.
- The selected focus now shows resolved grid coordinates such as `x 5 y 5`.
- Relative focuses also show stored relative offsets such as `dx -5 dy +5`.
- Kept badges limited to selected embedded focus nodes so technology and generic diagram nodes stay uncluttered.
- Styled badges as pointer-transparent overlays above the focus tile, so drag and keyboard interaction still belong to the node.
- Added English and Chinese locale keys for the badge templates.

## Verification

- Red test first: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx src/styles/diagram.test.ts` failed on the missing badge helper, missing canvas badge markup, and missing CSS block.
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx src/styles/diagram.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/layoutModel.test.ts src/diagramEditor/projectDiagram.test.ts src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/diagramHistory.test.ts src/diagramEditor/diagramImages.test.ts src/moduleEditor/diagramMetadata.test.ts src/moduleEditor/diagramSelection.test.ts src/projectModules.test.ts src/moduleEditor/model.test.ts src/styles/diagram.test.ts src/components/Workspace.test.tsx src/moduleEditor/ModuleEditor.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- Browser QA at `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html` through the in-app browser:
  - Selected `C08_REFORM` rendered `x 5 y 5 / dx -5 dy +5`.
  - Rendered 10 nodes, 10 edge paths, and 10 focus image or placeholder elements.
  - Normal-window geometry had no horizontal overflow.
  - Console warning/error count was 0.

## Next

- Continue improving direct manipulation: snapping preview labels during drag, branch drag handles, and a clearer before/after reflow preview for descendants.
