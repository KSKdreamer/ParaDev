# 2026-06-20 22:18 Focus Tile Plaque

## Context

The focus-tree canvas had the right grid scale and stepped routes, but each focus node still read too much like a generic diagram card. HOI4 focus trees are icon-first: each focus is a compact square icon tile with a small label plaque, while the node selection state stays separate from the icon frame.

## Changes

- Added a dedicated icon frame inside embedded focus nodes when an icon or generated placeholder is available.
- Added a compact title plaque at the bottom of embedded focus nodes so the label reads as part of the focus tile rather than a generic card title.
- Scoped outer node rectangle CSS selectors to direct children, preventing selection/search fills from recoloring the internal icon frame and title plaque.
- Kept the existing 3 x 3 grid footprint and node bounds unchanged so this visual pass does not disturb PIHC2-style `x`, `y`, `dx`, `dy`, `cx`, `cy`, `w`, or `priority` layout math.

## Verification

- Red check:
  - `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx src/styles/diagram.test.ts`
  - Failed before implementation because the focus icon frame/plaque markup and scoped CSS selectors were missing.
- Focused green:
  - `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx src/styles/diagram.test.ts`
  - `2 passed / 110 tests`.
- Broader desktop slice:
  - `rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts src/components/AppShell.test.tsx src/components/ProjectPanel.test.tsx src/components/Workspace.test.tsx src/moduleEditor/ModuleEditor.test.tsx src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/diagramImages.test.ts src/diagramEditor/diagramHistory.test.ts src/moduleEditor/diagramMetadata.test.ts src/styles/diagram.test.ts`
  - `14 passed / 299 tests`.
- Build:
  - `rtk npm --prefix apps/desktop run build`
  - Passed with the existing large-chunk warning.
- Browser QA:
  - Opened `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html?hoi4-plaque=1` at `1440 x 900`.
  - Confirmed focus nodes render as icon-first tiles with a separate icon frame and title plaque, while branch connectors and the inspector remain stable in a normal desktop window.
  - Fresh console check returned zero warnings/errors.

## Follow-Up

- The next fidelity slice should improve real focus icon asset selection and optional HOI4-style frame variants for focus status/type.
- Larger PIHC focus trees still need subtree move ergonomics beyond the current branch-drag and auto-layout controls.
