# 2026-06-20 22:14 Focus Tree Route Merge

## Context

The focus-tree canvas had HOI4-style stepped connectors, but PIHC focus data often carries both a visual tree parent and a prerequisite relationship for the same source/target pair. Rendering both relationships made the same route appear as stacked solid/dashed lines, which cluttered the focus grid.

## Changes

- Coalesced duplicate embedded-focus visual routes during projection:
  - if a focus source/target pair has both `tree` and `dependency` edges, the canvas draws the tree route once;
  - standalone prerequisite edges without a tree edge still render as prerequisite routes;
  - non-focus diagrams keep their original edge projection behavior.
- Kept the underlying `DiagramDocument.edges` unchanged, so edge counts, inspector relationship facts, metadata writeback, and JSON export still preserve the full relationship data.
- Updated render tests to assert that duplicate same-pair focus prerequisites count in the summary but do not draw as a second path.

## Verification

- Red check:
  - `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
  - Failed before implementation because the duplicate same-pair dependency route still rendered.
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
  - Opened `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html?hoi4-merge=1` at `1440 x 900`.
  - Confirmed duplicate tree/prerequisite overlays on the same focus pair were removed, standalone focus routes still rendered, and the toolbar/inspector layout remained stable.
  - Fresh console check returned zero warnings/errors.

## Follow-Up

- The next visual fidelity slice can make focus tiles more HOI4-like through icon plaques/frames without changing the data model.
- Larger PIHC trees may still need route trunk sharing across sibling branches; this slice only removes exact same-pair duplicate routes.
