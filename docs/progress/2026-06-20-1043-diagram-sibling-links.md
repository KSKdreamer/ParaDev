# 2026-06-20 10:43 - Diagram Sibling Links

## Scope

Improved the desktop focus-tree diagram selected-node panel for PIHC3. When a selected node has siblings, the panel now lists the other siblings as selectable links so users can move between neighboring focus branches before reordering or editing relationships.

## Changes

- Extended the selected sibling view state with sorted sibling ids.
- Reused the existing relationship-row renderer for selectable sibling links.
- Kept sibling link ordering tied to the same sorted order used by sibling reorder commands.
- Added English and Chinese translations for the sibling row and select action.
- Extended the static render coverage to assert sibling links exclude the current node and include sibling titles.

## Verification

- Red test first: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx` failed on the missing `Siblings` row.
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts src/moduleEditor/ModuleEditor.test.tsx src/moduleEditor/diagramSelection.test.ts src/moduleEditor/diagramMetadata.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- --run`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke on `http://127.0.0.1:5198/?smoke=sibling-links`: loaded the desktop shell, opened Technology, confirmed the startup overlay cleared, confirmed the expected plain-Vite SDK fallback, and saw only the React DevTools info console entry.
- `rtk git diff --check`

## Notes

Plain Vite still cannot load SDK-backed PIHC3 browser data, so the exact selected sibling links behavior is covered by the static React integration test rather than the browser smoke.

The Vite production build still emits the existing large-chunk warning for the editor bundles.

No Python files were changed in this slice, so the heaven-style Python scan was not applicable.
