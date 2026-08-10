# Focus Compact Image Canvas Progress

Date: 2026-06-21 00:57

Linear: TAL-000

## Done

- Made generated focus-tree diagram nodes default to a compact 2 x 2 grid footprint.
- Render compact focus nodes as image-first icon tiles using the migrated PIHC3 focus `preview.png` images, without canvas label plaques crowding the icons.
- Updated the diagram apply smoke fixture to use compact focus nodes backed by actual C08_PARTIV preview images.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/projectDiagram.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/diagramImages.test.ts src/diagramEditor/layoutModel.test.ts src/styles/diagram.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -k focus_asset_component -q`
- In-app browser smoke at `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html`: 9 focus images, 0 placeholders, max SVG icon size 34 px, no canvas focus labels, no horizontal body overflow.

## Risks Or Blockers

- The smoke fixture is still a compact representative tree, not the full C08_PARTIV project browser surface.
- Vite build still reports the existing large-chunk warning.

## Next

- Verify the full project browser focus-tree tab with a larger migrated PIHC3 tree and tune default viewport/fit behavior for dense trees.
