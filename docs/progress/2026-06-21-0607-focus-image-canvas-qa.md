# Focus Image Canvas QA Progress

Date: 2026-06-21 06:07

Linear: TAL-000

## Done

- Rechecked the migrated PIHC3 focus image path from `focus_tree` nodes to `focus_asset_component/.../preview.png`.
- Verified the source-backed focus canvas hydrates migrated preview PNGs through the binary-source thumbnail pipeline.
- Verified the apply-review focus canvas renders actual PIHC3 preview images, not placeholders, with 34-unit icons on the 48-unit focus grid.

## Verification

- `rtk bash -lc 'cd apps/desktop && npm run test:unit -- src/diagramEditor/projectDiagram.test.ts src/diagramEditor/diagramImages.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/ModuleEditor.test.tsx src/styles/diagram.test.ts'`
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'focus_tree_preview_icons_resolve or focus_asset_component'`
- `rtk git diff --check`
- `rtk bash -lc 'cd apps/desktop && npm run build'`
- Browser QA:
  - `http://127.0.0.1:5180/e2e/diagram-source-backed-smoke.html`: 6 hydrated focus images, 0 placeholders, `Images 6/6`.
  - `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html`: 9 actual focus images, 0 placeholders, 34-unit image slots on a 48-unit grid, image footprint under 2 grid cells.

## Risks Or Blockers

- Production build still reports the existing Vite large-chunk warning.
- The normal desktop project load can still take long enough that further progress/loading refinement remains useful.

## Next

- Continue the next usability slice from the startup/loading progress and large PIHC3 focus-tree opening workflow.
