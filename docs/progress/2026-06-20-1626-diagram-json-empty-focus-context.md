# 2026-06-20 16:26 - Diagram JSON empty focus context import

## Done

- Allowed diagram JSON draft import to add the first embedded focus node from an empty focus-tree context node.
- Kept the import boundary aligned with the UI root-focus insertion path, which already creates the same saveable draft shape.
- Added a guard that rejects new focus nodes whose project/source context payload differs from the current focus-tree context.

## Verification

- RED: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJsonImport.test.ts` rejected the first embedded focus node for an empty focus-tree context.
- GREEN: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJsonImport.test.ts`
- RED: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJsonImport.test.ts` accepted a new focus node with mismatched `relativeRoot` and `sourceRootRelativePath`.
- GREEN: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJsonImport.test.ts`
- Related: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/diagramMetadata.test.ts src/moduleEditor/diagramSelection.test.ts`
- Full desktop unit: `rtk npm --prefix apps/desktop run test:unit`
- Build: `rtk npm --prefix apps/desktop run build`

## Notes

- The Vite build still reports the existing large chunk warning for `SourceCodeEditor`, `index`, and `ImageDraftEditor`.
