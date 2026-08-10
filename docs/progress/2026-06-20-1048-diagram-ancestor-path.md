# 2026-06-20 10:48 - Diagram Ancestor Path

## Scope

Improved the desktop focus-tree diagram selected-node panel for PIHC3. When a selected focus node is deep in a branch, the panel now shows its ancestor path as selectable node links so users can jump back to the root or parent chain without hunting on the canvas.

## Changes

- Added cycle-safe ancestor id derivation for the selected diagram node.
- Reused the existing relationship-row renderer for selectable ancestor path links.
- Kept the path read-only and UI-only; no persistence or metadata-write behavior changed.
- Added English and Chinese translations for the path row and ancestor selection label.
- Extended static render coverage for a selected embedded PIHC3 focus node with a root-to-parent path.

## Verification

- Red test first: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx` failed on the missing `Select ancestor` path links.
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts src/moduleEditor/ModuleEditor.test.tsx src/moduleEditor/diagramSelection.test.ts src/moduleEditor/diagramMetadata.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- --run`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke on `http://127.0.0.1:5199/?smoke=ancestor-path`: loaded the desktop shell, opened Technology, confirmed the startup overlay cleared, confirmed the expected plain-Vite SDK fallback, captured screenshot evidence through the in-app Browser, and saw zero warning/error logs.
- `rtk git diff --check`

## Notes

Plain Vite still cannot load SDK-backed PIHC3 browser data, so the exact selected ancestor path behavior is covered by the static React integration test rather than the browser smoke.

The Vite production build still emits the existing large-chunk warning for the editor bundles.

No Python files were changed in this slice, so the heaven-style Python scan was not applicable.
