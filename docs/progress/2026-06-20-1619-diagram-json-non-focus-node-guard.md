# 2026-06-20 16:19 - Diagram JSON non-focus node guard

## Done

- Added diagram JSON draft import guards that reject added or removed non-focus source nodes.
- Covered the PIHC3 technology/source-entity cases where pasted JSON could create a duplicate non-focus node or hide an existing source node that the metadata writer cannot persist.
- Kept existing behavior for moving/relinking existing browser nodes and for adding embedded focus nodes.

## Verification

- RED: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJsonImport.test.ts` failed because `TECH_FIREARM_COPY` was accepted into diagram history.
- RED: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJsonImport.test.ts` failed because removing `TECH_FIREARM` was accepted into diagram history.
- GREEN: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJsonImport.test.ts`
- Related: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/diagramMetadata.test.ts src/moduleEditor/diagramSelection.test.ts`
- Full desktop unit: `rtk npm --prefix apps/desktop run test:unit`
- Build: `rtk npm --prefix apps/desktop run build`

## Notes

- The Vite build still reports the existing large chunk warning for `SourceCodeEditor`, `index`, and `ImageDraftEditor`.
