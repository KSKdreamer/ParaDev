# 2026-06-20 16:37 - Diagram JSON focus relationship endpoints

## Done

- Rejected imported dependency/reference edges that connect an embedded focus node to a non-focus metadata/context node.
- Kept technology and generic non-focus relationships valid by applying the guard only when exactly one endpoint is an embedded focus.
- Added coverage for the empty PIHC3 focus-tree context workflow, where a copied JSON edge could otherwise point `FOCUS_NEW_ROOT` at the unsavable `C08_PARTIV` context node.

## Verification

- RED: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJsonImport.test.ts` accepted `dependency:C08_PARTIV->FOCUS_NEW_ROOT`.
- GREEN: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJsonImport.test.ts`
- Related: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/diagramMetadata.test.ts src/moduleEditor/diagramSelection.test.ts`
- Full desktop unit: `rtk npm --prefix apps/desktop run test:unit`
- Build: `rtk npm --prefix apps/desktop run build`

## Notes

- The Vite build still reports the existing large chunk warning for `SourceCodeEditor`, `index`, and `ImageDraftEditor`.
