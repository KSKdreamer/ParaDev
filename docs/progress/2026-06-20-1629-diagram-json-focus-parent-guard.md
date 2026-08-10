# 2026-06-20 16:29 - Diagram JSON focus parent guard

## Done

- Added a diagram JSON draft import guard that rejects embedded focus nodes parented to non-focus context nodes.
- Kept JSON import aligned with the GUI behavior: empty focus-tree context nodes can create root focuses, while child focuses require an embedded focus parent.
- Prevented imported empty-tree drafts from writing a focus prerequisite or parent that points at the focus-tree module id.

## Verification

- RED: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJsonImport.test.ts` accepted `FOCUS_NEW_CHILD` under non-focus parent `C08_PARTIV`.
- GREEN: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJsonImport.test.ts`
- Related: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/diagramMetadata.test.ts src/moduleEditor/diagramSelection.test.ts`
- Full desktop unit: `rtk npm --prefix apps/desktop run test:unit`
- Build: `rtk npm --prefix apps/desktop run build`

## Notes

- The Vite build still reports the existing large chunk warning for `SourceCodeEditor`, `index`, and `ImageDraftEditor`.
