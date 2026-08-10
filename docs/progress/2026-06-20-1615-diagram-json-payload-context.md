# Diagram JSON Payload Context Progress

Date: 2026-06-20 16:15

Linear: TAL-000

## Done

- Added a diagram JSON draft-import regression test for existing nodes whose ParaDev source-context payload changes.
- Rejected imported existing-node payload changes across stable project, family, module, source root, and embedded focus fields before they can enter diagram history.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJsonImport.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/diagramMetadata.test.ts src/moduleEditor/diagramSelection.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`

## Risks Or Blockers

- Desktop build still reports the existing Vite large-chunk warning.

## Next

- Continue hardening diagram editor import/apply flows and PIHC3-backed metadata updates.
