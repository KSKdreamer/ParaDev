# 2026-06-20 16:50 - Layout model focus child insert guard

## Done

- Rejected direct child insertion that mixes embedded focus nodes with non-focus context nodes.
- Preserved valid focus-to-focus child insertion and the existing root insertion flow for empty focus trees.
- Added layout model coverage for the PIHC3 focus-tree context case so `insertDiagramChildNode` cannot create `tree:C08_PARTIV->FOCUS_NEW_CHILD`.

## Verification

- RED: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/layoutModel.test.ts` accepted `tree:C08_PARTIV->FOCUS_NEW_CHILD`.
- GREEN: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/layoutModel.test.ts`
- Related: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/diagramMetadata.test.ts src/moduleEditor/diagramSelection.test.ts`
- Full desktop unit: `rtk npm --prefix apps/desktop run test:unit`
- Build: `rtk npm --prefix apps/desktop run build`

## Notes

- The Vite build still reports the existing large chunk warning for `SourceCodeEditor`, `index`, and `ImageDraftEditor`.
