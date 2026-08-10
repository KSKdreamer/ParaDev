# Diagram candidate labels

## Slice

Improved the focus/technology diagram relationship editor so parent, prerequisite, and reference quick-candidate controls carry both the stable node id and the readable node title. The submitted value remains the id, which keeps layout and metadata writes unchanged, but PIHC3 users no longer have to choose from opaque ids alone when a title is available.

Also pinned metadata coverage for adding a PIHC3 technology dependency when the target metadata starts with an inline empty `dependency_ids: []` list.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/ModuleEditor.test.tsx src/moduleEditor/diagramMetadata.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- --run`
- `rtk npm --prefix apps/desktop run build`
- `rtk git diff --check`

Browser smoke opened `http://127.0.0.1:5188/?smoke=diagram-candidate-labels`, loaded the configured PIHC3 desktop shell, opened the Technology family, and reported zero browser warnings/errors. Plain Vite still shows the expected `SDK browser unavailable` fallback instead of the SDK-backed diagram data, so the exact candidate-label DOM is covered by the component render test.

## Notes

- No Python paths changed; the heaven-style Python scan was not applicable for this GUI-only slice.
- The workspace remains dirty with many unrelated tracked and untracked files; no staging or commit was performed.
