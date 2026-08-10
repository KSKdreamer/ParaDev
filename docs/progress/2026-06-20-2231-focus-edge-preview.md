# 2026-06-20 22:31 Focus Edge Preview

## Context

Branch drag preview now moves the affected focus nodes, but connectors were still projected from the original resolved positions until pointer release. That made HOI4-style branch movement feel visually split: focus tiles moved, while their tree lines stayed behind.

## Changes

- Exported `projectDiagram` for focused projection tests.
- Added optional drag-preview projection input with affected node ids and a pixel offset.
- Shifted a lightweight copy of the affected resolved nodes for edge projection only, keeping the real resolved node list stable for selection, search, inspector facts, minimap, and layout state.
- Wired `ProjectDiagramView` to compute drag-preview ids and offsets before projection, so branch connector paths follow the same temporary node movement as the focus tiles.

## Verification

- Red check:
  - `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
  - Failed before implementation because `projectDiagram` was not exported and did not accept drag-preview inputs.
- Focused green:
  - `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
  - `1 passed / 108 tests`.
- Broader desktop slice:
  - `rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts src/components/AppShell.test.tsx src/components/ProjectPanel.test.tsx src/components/Workspace.test.tsx src/moduleEditor/ModuleEditor.test.tsx src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/diagramImages.test.ts src/diagramEditor/diagramHistory.test.ts src/moduleEditor/diagramMetadata.test.ts src/styles/diagram.test.ts`
  - `14 passed / 301 tests`.
- Build:
  - `rtk npm --prefix apps/desktop run build`
  - Passed with the existing large-chunk warning.
- Browser QA:
  - Opened `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html?edge-preview=1` at `1440 x 900`.
  - Confirmed the focus grid, plaques, branch connectors, inspector, and minimap still render correctly.
  - DOM inspection found `10` focus nodes and `10` projected connector paths in the smoke diagram.
  - Fresh console check returned zero warnings/errors.

## Follow-Up

- Larger PIHC focus trees still need clearer branch-mode discovery and possibly an explicit branch-selection affordance beyond modifier keys.
- Drag previews could add a subtle branch ghost or edge highlight, but the current slice keeps the data model and visual styling minimal.
