# Diagram JSON Canonical Edge IDs Progress

Date: 2026-06-20 16:02

Linear: TAL-000

## Done

- Added a diagram JSON import regression test for edges whose IDs disagree with their kind, source, and target.
- Rejected non-canonical imported edge IDs after duplicate edge ID and duplicate relationship checks.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJson.test.ts src/diagramEditor/layoutModel.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/diagramMetadata.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`

## Risks Or Blockers

- Desktop build still reports the existing Vite large-chunk warning.

## Next

- Continue hardening diagram import/export invariants and PIHC3-backed editor workflows.
