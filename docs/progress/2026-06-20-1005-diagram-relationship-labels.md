# Diagram relationship labels

## Slice

Improved the focus/technology diagram selection panel so existing prerequisite, unlock, and reference rows show both the stable node id and the readable node title. Select and remove actions still dispatch raw ids, so metadata writes and layout commands keep the same stable identifiers while PIHC3 users get readable context in the editor.

This extends the previous quick-candidate label work from add controls to existing relationship context.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/ModuleEditor.test.tsx src/moduleEditor/diagramMetadata.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- --run`
- `rtk npm --prefix apps/desktop run build`
- `rtk git diff --check`

Browser smoke opened `http://127.0.0.1:5189/?smoke=diagram-relationship-labels`, loaded the configured PIHC3 shell, opened the Technology family, and reported zero browser warnings/errors. Plain Vite still shows the expected `SDK browser unavailable` fallback instead of SDK-backed diagram data, so the exact relationship-label DOM is covered by `ProjectDiagramView` render tests.

## Notes

- No Python paths changed; the heaven-style Python scan was not applicable for this GUI-only slice.
- The workspace remains dirty with unrelated tracked and untracked files; no staging or commit was performed.
