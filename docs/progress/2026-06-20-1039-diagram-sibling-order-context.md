# 2026-06-20 10:39 - Diagram Sibling Order Context

## Scope

Improved the desktop focus-tree diagram selected-node panel for PIHC3. When a selected node has siblings, the panel now shows its sorted sibling position so users can understand reorder context before moving the node earlier or later.

## Changes

- Extended the existing sibling reorder view state with the selected node's sibling index and sibling count.
- Rendered a compact selected-node sibling summary when a node has more than one sibling.
- Added English and Chinese translations for the sibling order text.
- Kept the summary tied to the same sorted sibling order used by the reorder controls.
- Added focused static render coverage for the selected sibling summary.

## Verification

- Red test first: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx` failed on the missing `project-diagram-selection-sibling` marker.
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts src/moduleEditor/ModuleEditor.test.tsx src/moduleEditor/diagramSelection.test.ts src/moduleEditor/diagramMetadata.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- --run`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke on `http://127.0.0.1:5197/?smoke=sibling-order-context`: loaded the desktop shell, opened Technology, confirmed the startup overlay cleared, confirmed the expected plain-Vite SDK fallback, captured `/tmp/paradev-sibling-order-smoke.png`, and saw only the React DevTools info console entry.
- `rtk git diff --check`

## Notes

Plain Vite still cannot load SDK-backed PIHC3 browser data, so the exact selected sibling order behavior is covered by the static React integration test rather than the browser smoke.

The Vite production build still emits the existing large-chunk warning for the editor bundles.

No Python files were changed in this slice, so the heaven-style Python scan was not applicable.
