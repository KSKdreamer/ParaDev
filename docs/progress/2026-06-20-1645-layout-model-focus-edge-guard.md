# 2026-06-20 16:45 - Layout model focus edge guard

## Done

- Rejected direct dependency/reference setter calls that mix embedded focus nodes with non-focus context nodes.
- Preserved valid focus-to-focus and non-focus-to-non-focus relationship edges.
- Added layout model coverage for the empty PIHC3 focus-tree context case so `C08_PARTIV` cannot become a prerequisite or mutual-exclusion endpoint through direct model calls.

## Verification

- RED: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/layoutModel.test.ts` accepted mixed focus/context dependency and reference edges.
- GREEN: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/layoutModel.test.ts`
- Related: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/diagramMetadata.test.ts src/moduleEditor/diagramSelection.test.ts`
- Full desktop unit: `rtk npm --prefix apps/desktop run test:unit`
- Build: `rtk npm --prefix apps/desktop run build`

## Notes

- The Vite build still reports the existing large chunk warning for `SourceCodeEditor`, `index`, and `ImageDraftEditor`.
