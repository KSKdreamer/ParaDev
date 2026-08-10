# Diagram JSON Focus Embedded ID Progress

Date: 2026-06-20 16:12

Linear: TAL-000

## Done

- Added diagram JSON draft-import regression tests for missing and mismatched focus `embeddedId` payloads.
- Rejected imported focus nodes whose ParaDev payload cannot be tied back to the actual diagram node id.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJsonImport.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/diagramMetadata.test.ts src/moduleEditor/diagramSelection.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`

## Risks Or Blockers

- Desktop build still reports the existing Vite large-chunk warning.

## Next

- Continue tightening the diagram editor save boundary and PIHC3-backed metadata workflows.
