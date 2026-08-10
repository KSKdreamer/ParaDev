# Focus Move Footprint Progress

Date: 2026-06-21 03:06

Linear: TAL-000

## Done

- Added selected-node movement footprint feedback to the focus diagram inspector so users can see the active branch, node-only, or descendant-relayout move scope before dragging.
- Reused the existing affected-node computation to show the impacted focus IDs as compact selectable chips without changing the underlying move behavior.
- Added English and Chinese labels plus layout styling that keeps the inspector compact in normal desktop windows.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx src/styles/diagram.test.ts`
- `rtk git diff --check`
- `rtk npm --prefix apps/desktop run build`
- Browser QA at `http://127.0.0.1:5180/e2e/diagram-move-smoke.html`: 6 migrated PIHC3 preview PNG images, 0 placeholders, 48 px focus-slot grid, 34 px focus images, branch footprint shows 4 affected focus IDs, no console warnings/errors.

## Risks Or Blockers

- This is still a rendered desktop-web smoke rather than a packaged Tauri E2E test.

## Next

- Continue improving large-tree navigation and branch reflow ergonomics on real PIHC3 focus trees.
