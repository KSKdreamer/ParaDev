# 2026-06-20 16:32 - Focus context candidate filter

## Done

- Filtered relationship candidates for embedded focus nodes so non-focus focus-tree context nodes are not offered as parent, prerequisite, or reference targets.
- Kept generic and technology diagram candidate behavior unchanged; the filter applies only when the selected node is an embedded focus.
- Added render coverage for an empty focus-tree context plus newly inserted root focus, matching the PIHC3 first-focus workflow.

## Verification

- RED: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx` offered `C08_PARTIV` as a parent/prerequisite/reference candidate for `FOCUS_NEW_ROOT`.
- GREEN: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
- Related: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/diagramMetadata.test.ts src/moduleEditor/diagramSelection.test.ts`
- Full desktop unit: `rtk npm --prefix apps/desktop run test:unit`
- Build: `rtk npm --prefix apps/desktop run build`

## Notes

- The Vite build still reports the existing large chunk warning for `SourceCodeEditor`, `index`, and `ImageDraftEditor`.
