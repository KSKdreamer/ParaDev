# 2026-06-20 16:42 - Diagram metadata focus parent filter

## Done

- Filtered PIHC3 focus parent metadata writes so only embedded focus node ids can become persisted focus parents/prerequisites.
- Prevented directly constructed drafts from serializing the focus-tree context node `C08_PARTIV` as the parent of a new embedded focus.
- Added writer-side coverage for an empty focus-tree draft with a bad `parentId`/tree edge to the non-focus context node.

## Verification

- RED: `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts` wrote `C08_PARTIV` into the new focus `prerequisites` list.
- GREEN: `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts`
- Related: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/diagramMetadata.test.ts src/moduleEditor/diagramSelection.test.ts`
- Full desktop unit: `rtk npm --prefix apps/desktop run test:unit`
- Build: `rtk npm --prefix apps/desktop run build`

## Notes

- The Vite build still reports the existing large chunk warning for `SourceCodeEditor`, `index`, and `ImageDraftEditor`.
