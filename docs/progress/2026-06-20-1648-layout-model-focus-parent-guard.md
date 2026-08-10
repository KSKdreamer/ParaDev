# 2026-06-20 16:48 - Layout model focus parent guard

## Done

- Rejected direct tree-parent setter calls that mix embedded focus nodes with non-focus context nodes.
- Preserved valid focus-to-focus tree parent changes and kept parent clearing available for recovery.
- Added layout model coverage for the PIHC3 empty focus-tree context case so `C08_PARTIV` cannot become a focus parent through direct model calls.

## Verification

- RED: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/layoutModel.test.ts` accepted `tree:C08_PARTIV->FOCUS_CHILD`.
- GREEN: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/layoutModel.test.ts`
- Related: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/diagramMetadata.test.ts src/moduleEditor/diagramSelection.test.ts`
- Full desktop unit: `rtk npm --prefix apps/desktop run test:unit`
- Build: `rtk npm --prefix apps/desktop run build`

## Notes

- The Vite build still reports the existing large chunk warning for `SourceCodeEditor`, `index`, and `ImageDraftEditor`.
