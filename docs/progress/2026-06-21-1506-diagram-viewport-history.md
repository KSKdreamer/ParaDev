# Diagram Viewport History Progress

Date: 2026-06-21 15:06

Linear: TAL-000

## Done

- Added an ephemeral diagram-history update path for viewport-only changes.
- Routed diagram viewport saves through the ephemeral path so pan, zoom, search-centering, and minimap navigation can restore the current view without adding Undo steps.
- Kept regular node, edge, layout, import, and apply-review edits on the normal undoable history path.

## Verification

- Red: `rtk npm --prefix apps/desktop exec vitest run src/diagramEditor/diagramHistory.test.ts` failed before `applyDiagramPresentUpdate` existed.
- Green: `rtk npm --prefix apps/desktop exec vitest run src/diagramEditor/diagramHistory.test.ts`.
- Green: `rtk npm --prefix apps/desktop exec vitest run src/diagramEditor/diagramHistory.test.ts src/diagramEditor/layoutModel.test.ts src/moduleEditor/ModuleEditor.test.tsx src/diagramEditor/ProjectDiagramView.test.tsx src/styles/diagram.test.ts e2e/diagram-tab-smoke-state.test.ts`.
- Green: `rtk npm --prefix apps/desktop run build` with the existing Vite large-chunk warning.
- Browser smoke: `http://127.0.0.1:5180/e2e/diagram-tab-smoke.html` opened C01 Main, rendered 83 nodes and 83 images, dragged the minimap, changed the main SVG `viewBox`, kept Undo disabled, showed no dirty summary or apply-review UI, and reported no console warnings or errors.

## Risks Or Blockers

- Redo behavior after panning while already sitting on an undone history state may need a later explicit UX decision; the primary clean and edited viewport paths are covered.

## Next

- Continue improving large-tree editing feedback: minimap affordance styling, search-result stepping visibility, and source-backed apply-review clarity.
