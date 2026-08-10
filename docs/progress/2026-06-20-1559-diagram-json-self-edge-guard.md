# Diagram JSON Self-Edge Guard Progress

Date: 2026-06-20 15:59

Linear: TAL-000

## Done

- Added a diagram JSON import regression test for self-targeting edges.
- Rejected imported edges whose source and target are the same node before graph layout validation.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJson.test.ts src/diagramEditor/layoutModel.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/diagramMetadata.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`

## Risks Or Blockers

- Desktop build still reports the existing Vite large-chunk warning.

## Next

- Continue tightening diagram import/export invariants and PIHC3-backed editor workflows.
