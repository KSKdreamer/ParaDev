# 2026-06-20 16:54 - Layout model source node delete guard

## Done

- Rejected subtree and node-only deletion for source-backed non-focus diagram nodes.
- Preserved generic diagram deletion and embedded focus deletion, so PIHC3 users can still remove focus nodes while context/technology source nodes remain stable.
- Added layout model coverage for the PIHC3 focus-tree context case so `C08_PARTIV` cannot be removed through direct model calls.

## Verification

- RED: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/layoutModel.test.ts` removed `C08_PARTIV` through both subtree and node-only deletion.
- GREEN: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/layoutModel.test.ts`
- Related: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/diagramMetadata.test.ts src/moduleEditor/diagramSelection.test.ts`
- Full desktop unit: `rtk npm --prefix apps/desktop run test:unit`
- Build: `rtk npm --prefix apps/desktop run build`

## Notes

- The Vite build still reports the existing large chunk warning for `SourceCodeEditor`, `index`, and `ImageDraftEditor`.
