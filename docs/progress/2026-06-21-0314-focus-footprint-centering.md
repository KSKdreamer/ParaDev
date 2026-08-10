# Focus Footprint Centering Progress

Date: 2026-06-21 03:14

Linear: TAL-000

## Done

- Added a selected-node inspector action that centers the current move footprint, so users can quickly bring a branch, node-only scope, or descendant-relayout scope into view before moving it.
- Added `panOffsetToCenterNodes(...)` to center viewports from combined node bounds instead of only a single node.
- Kept the control compact inside the existing move-footprint panel and localized the label in English and Chinese.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx src/styles/diagram.test.ts`
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k "focus_tree_preview_icons or focus_asset_component"`
- `rtk npm --prefix apps/desktop run build`
- `rtk git diff --check`
- Browser QA at `http://127.0.0.1:5180/e2e/diagram-move-smoke.html`: 6 PIHC3 preview PNG focus images at 34 x 34 on a 48 px grid, 0 placeholders, one `Center move footprint` control, canvas viewBox changed from `-38.344 -48 1228.687 528` to `-110.343 0 1228.687 528` after click, no console warnings/errors.

## Risks Or Blockers

- The check remains a Vite rendered smoke page rather than a packaged Tauri E2E run.

## Next

- Continue improving large real-tree ergonomics, especially branch reflow previews and normal-window interaction polish.
