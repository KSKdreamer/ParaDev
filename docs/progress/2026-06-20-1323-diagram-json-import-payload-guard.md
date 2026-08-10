# 2026-06-20 13:23 - Diagram JSON Import Payload Guard

## Context

The diagram JSON import path accepted schema-valid diagrams even when nodes omitted or remapped the ParaDev metadata payload used by the apply path. That could leave the GUI showing an imported draft that was not safe to write back to PIHC3 metadata.

## Changes

- Added import-draft compatibility validation for payload-backed project diagrams.
- Rejected imported nodes missing `itemId` / `objectId` payload metadata.
- Rejected imported nodes whose `itemId` points outside the current diagram's metadata entities.
- Rejected existing nodes whose project payload is remapped away from the current diagram.
- Updated the valid import fixture to preserve payload metadata while changing layout.

## Verification

- Red: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJsonImport.test.ts`
  - Failed before implementation because a missing-payload import was accepted as a changed draft.
- Focused green: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJsonImport.test.ts`
  - 4 passed.
- Related: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/diagramJson.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/layoutModel.test.ts src/moduleEditor/ModuleEditor.test.tsx src/moduleEditor/diagramMetadata.test.ts`
  - 173 passed.
- Build: `rtk npm --prefix apps/desktop run build`
  - Passed with the existing Vite large-chunk warning.
- Whitespace: `rtk rg -n "[ \t]+$" apps/desktop/src/diagramEditor/diagramJsonImport.ts apps/desktop/src/diagramEditor/diagramJsonImport.test.ts`
  - No trailing whitespace.

## Notes

This keeps import/export useful for advanced diagram edits while preventing stale or foreign JSON from silently entering the PIHC3 write path.
