# 2026-06-20 13:26 - Diagram JSON Import Object Guard

## Context

The diagram JSON import payload guard rejected missing and foreign `itemId` metadata, but a new imported focus node could still reuse the current focus tree `itemId` while carrying a foreign `objectId`. That should not enter the PIHC3 metadata write path.

## Changes

- Tightened import compatibility to validate the current diagram's payload tuple: `itemId`, `objectId`, and `embeddedKind`.
- Rejected imported nodes whose metadata object is outside the current metadata entity.
- Added a regression case for a new imported focus node with `itemId: focus_tree:C08` and `objectId: C09`.

## Verification

- Red: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJsonImport.test.ts`
  - Failed before implementation because the import was accepted as a changed draft.
- Focused green: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJsonImport.test.ts`
  - 4 passed.
- Related: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/diagramJson.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/layoutModel.test.ts src/moduleEditor/ModuleEditor.test.tsx src/moduleEditor/diagramMetadata.test.ts`
  - 173 passed.
- Build: `rtk npm --prefix apps/desktop run build`
  - Passed with the existing Vite large-chunk warning.
- Whitespace: `rtk rg -n "[ \t]+$" apps/desktop/src/diagramEditor/diagramJsonImport.ts apps/desktop/src/diagramEditor/diagramJsonImport.test.ts`
  - No trailing whitespace.

## Notes

This narrows the advanced JSON import surface to diagrams that still target the same PIHC3 metadata objects the GUI can safely apply.
