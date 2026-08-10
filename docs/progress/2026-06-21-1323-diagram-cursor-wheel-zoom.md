# Diagram Cursor Wheel Zoom Progress

Date: 2026-06-21 13:23

Linear: TAL-000

## Done

- Changed diagram Ctrl + mouse wheel zoom to anchor at the cursor instead of preserving the old pan offset.
- Added a small exported viewport helper for keeping a cursor point at the same relative position while moving between zoom levels.
- Shared SVG client-point conversion between pointer panning and wheel zooming.

## Verification

- Red test first: `rtk npm --prefix apps/desktop exec vitest run src/diagramEditor/ProjectDiagramView.test.tsx` failed because `panOffsetForZoomAtPoint` did not exist.
- `rtk npm --prefix apps/desktop exec vitest run src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop exec vitest run e2e/diagram-tab-smoke-state.test.ts e2e/source-backed-focus-image-bridge.test.ts src/diagramEditor/sourceBackedSmokeModel.test.ts src/moduleEditor/sourceBackedDiagramApplySmokeModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/styles/diagram.test.ts`
- `rtk npm --prefix apps/desktop run build`
- Browser health check at `http://127.0.0.1:5180/e2e/diagram-tab-smoke.html`: focus-tree tab active, 83 focus images rendered, `Images 83/83`, and console warnings/errors empty.

## Risks Or Blockers

- The in-app browser wrapper can verify render health but did not expose event constructors or locator dispatch for a full synthetic wheel-event smoke. The cursor-anchor behavior is unit-covered and the React handler is type-checked in the production build.
- The production build still emits the existing Vite large-chunk warning.

## Next

- Keep improving focus-tree navigation ergonomics around panning, minimap targeting, and selected-node jumps.
