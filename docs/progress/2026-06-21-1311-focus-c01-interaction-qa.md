# Focus C01 Interaction QA Progress

Date: 2026-06-21 13:11

Linear: TAL-000

## Done

- Rechecked the full C01_MAIN focus-tree diagram tab after the grid-density, DPI, simplified-toolbar, and source-backed image work.
- Added a fallback node open decision so SVG focus nodes can open the read-only info popover from native double-clicks or rapid no-move click sequences even when drag pointer handling suppresses ordinary click events.
- Kept the focus-tree page minimal: advanced file/layout/node/pan toolbar groups and the old selection inspector remain hidden for focus diagrams.

## Verification

- `rtk npm --prefix apps/desktop exec vitest run e2e/diagram-tab-smoke-state.test.ts e2e/source-backed-focus-image-bridge.test.ts src/diagramEditor/sourceBackedSmokeModel.test.ts src/moduleEditor/sourceBackedDiagramApplySmokeModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/styles/diagram.test.ts`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke at `http://127.0.0.1:5180/e2e/diagram-tab-smoke.html`: confirmed one separate diagram tab, 83 C01 nodes, 83/83 data URL focus images, zero placeholders, 72 x 72 px images inside 96 px focus slots, 48 px visible grid, black 1 px connection lines, zero arrow markers, hidden selection panel/advanced groups, selected-node mode switch from auto to relative, review-then-apply writing two C01 source edits, and double-click popup for `FOCUS_C01_DEM_CHANGE` with `src/modules/focus_tree/C01_MAIN/legacy/C01_DEM_CHANGE/info.json`.

## Risks Or Blockers

- The in-app CUA two-click helper spaces synthetic clicks differently from a human double-click, so final popup verification used Playwright locator `dblclick` on the SVG hitbox.
- The production build still emits the existing Vite large-chunk warning.

## Next

- Keep iterating on relationship editing affordances and future module-tab jump behavior from the focus info popup.
