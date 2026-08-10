# 2026-06-20 22:11 Focus Tree Edge Routing

## Context

The focus-tree editor had moved to square focus icon tiles, but the links still used generic graph-style Bezier curves. HOI4 focus trees read as grid-routed focus lines, so the connector geometry needed to follow the tile grid.

## Changes

- Added focus-only edge routing in `ProjectDiagramView`:
  - embedded focus tree and prerequisite links now use stepped vertical-horizontal-vertical paths;
  - embedded focus reference links now connect side-to-side between neighboring focus tiles;
  - non-focus module and technology diagrams keep the existing cubic edge projection.
- Added render regressions proving both behaviors:
  - non-focus edges stay cubic;
  - embedded focus tree/prerequisite/reference edges use the new routed path shapes.

## Verification

- Red check:
  - `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
  - Failed on the new stepped focus-route expectations before implementation.
- Focused green:
  - `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
  - `1 passed / 106 tests`.
- Broader desktop slice:
  - `rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts src/components/AppShell.test.tsx src/components/ProjectPanel.test.tsx src/components/Workspace.test.tsx src/moduleEditor/ModuleEditor.test.tsx src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/diagramImages.test.ts src/diagramEditor/diagramHistory.test.ts src/moduleEditor/diagramMetadata.test.ts src/styles/diagram.test.ts`
  - `14 passed / 298 tests`.
- Build:
  - `rtk npm --prefix apps/desktop run build`
  - Passed with the existing large-chunk warning.
- Browser QA:
  - Opened `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html?hoi4-route=1` at `1440 x 900`.
  - Confirmed tree/prereq links route through square elbows on the focus grid, reference links connect side-to-side, and toolbar/inspector layout remains stable.
  - Fresh console check returned zero warnings/errors.

## Follow-Up

- Route merging could become smarter later, so shared trunk lines for sibling prerequisites look closer to in-game HOI4 trees instead of parallel tree/prereq overlays.
- A later visual pass should replace the simple focus tile frame with a more HOI4-like focus plaque treatment while preserving this routing contract.
