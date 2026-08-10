# Diagram Minimap Drag Progress

Date: 2026-06-21 15:00

Linear: TAL-000

## Done

- Added continuous minimap drag panning for large focus and technology diagrams.
- Captured the active minimap pointer so only the initiating drag moves the canvas viewport.
- Kept keyboard minimap centering and click-to-jump behavior intact.

## Verification

- Red: `rtk npm --prefix apps/desktop exec vitest run src/diagramEditor/ProjectDiagramView.test.tsx` failed before the minimap drag helpers existed.
- Green: `rtk npm --prefix apps/desktop exec vitest run src/diagramEditor/ProjectDiagramView.test.tsx`.
- Green: `rtk npm --prefix apps/desktop exec vitest run src/diagramEditor/ProjectDiagramView.test.tsx src/styles/diagram.test.ts e2e/diagram-tab-smoke-state.test.ts`.
- Green: `rtk npm --prefix apps/desktop run build` with the existing Vite large-chunk warning.
- Browser smoke: `http://127.0.0.1:5180/e2e/diagram-tab-smoke.html` opened the National Focuses diagram, rendered C01 Main with 83 nodes and 83 images, dragged the minimap through Browser CUA, changed the main SVG `viewBox` from `-48 -902.869 3456 3437.738` to `1378.296 -902.869 3456 3437.738`, and reported no console warnings or errors.

## Risks Or Blockers

- Browser smoke covers the rendered C01 path; touch-device and trackpad-specific minimap gestures still need a later manual pass.

## Next

- Continue tightening large-tree navigation around saved viewport restore, minimap affordance styling, and search-result stepping visibility.
