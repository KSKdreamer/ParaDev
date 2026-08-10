# 2026-06-20 16:40 - Diagram metadata focus relationship filter

## Done

- Filtered metadata relationship drafts so PIHC3 focus prerequisites and mutual exclusions only persist embedded focus node ids.
- Prevented non-focus focus-tree context nodes from emitting technology-style `path_target_ids` when a bad draft edge targets an embedded focus.
- Added writer-side coverage for a directly constructed empty focus-tree draft containing invalid dependency/reference edges to `C08_PARTIV`.

## Verification

- RED: `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts` wrote `C08_PARTIV` into prerequisites, `path_target_ids`, and mutually exclusive output.
- GREEN: `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts`
- Related: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/diagramMetadata.test.ts src/moduleEditor/diagramSelection.test.ts`
- Full desktop unit: `rtk npm --prefix apps/desktop run test:unit`
- Build: `rtk npm --prefix apps/desktop run build`

## Notes

- The Vite build still reports the existing large chunk warning for `SourceCodeEditor`, `index`, and `ImageDraftEditor`.
