# Root focus branch delete

## Slice

- Enabled root focus branch removal in the diagram toolbar so users can delete an entire root branch, not only non-root branches.
- Kept dirty Apply/Discard controls visible when a draft diagram becomes empty after deleting the last focus branch.
- Kept focus and technology diagram panels mounted for empty draft diagrams in the module editor.
- Added PIHC3 metadata coverage for deleting a root focus branch down to an empty `settings.focuses` block.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/ModuleEditor.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/ModuleEditor.test.tsx src/moduleEditor/diagramMetadata.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- --run`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke at `http://127.0.0.1:5187/`: app loaded, module row interaction worked, no Vite overlay, and no console warnings/errors.

## Notes

- Plain Vite cannot load SDK project browser data, so the rendered smoke reaches the expected `SDK browser unavailable` fallback after opening the focus module. Diagram-specific behavior is covered by unit tests in this environment.
- No Python paths changed in this slice, so the heaven-style Python scan was not applicable.
- The workspace already contains many unrelated modified and untracked files; no files were staged or committed.
