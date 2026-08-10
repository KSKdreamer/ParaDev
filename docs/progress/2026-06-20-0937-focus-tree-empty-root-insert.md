# Focus tree empty root insert

## Slice

- Enabled the diagram toolbar to add a root focus when a focus-tree module has only its context node and no embedded focus records yet.
- Added the module-editor draft input path that turns that focus-tree context node into a new embedded root focus draft.
- Added PIHC3 metadata coverage for writing the first root focus into an empty `settings.focuses` block.
- Normalized inline empty `focuses: []` metadata before inserting the first root focus entry.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/ModuleEditor.test.tsx src/moduleEditor/diagramMetadata.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- --run`
- `rtk npm --prefix apps/desktop run build`
- `rtk git diff --check`

## Notes

- No Python paths changed in this slice, so the heaven-style Python scan was not applicable.
- The workspace already contains many unrelated modified and untracked files; no files were staged or committed.
