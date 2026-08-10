# Focus Actual Image Canvas Progress

Date: 2026-06-21 06:55

Linear: TAL-000

## Done

- Rechecked PIHC3 focus image migration through `focus_asset_component/.../preview.png` and the C08 source-backed/apply-review canvas paths.
- Verified the live SVG canvas renders real focus images, not placeholders, at 34 units inside 48-unit focus slots.
- Tightened the source-backed clear-parent apply smoke model so it has source-root/meta-slot metadata and writes `parent: null` plus absolute `x`/`y` to PIHC `legacy/<focus>/info.json`.

## Verification

- `rtk npm run test:unit -- src/moduleEditor/sourceBackedDiagramApplySmokeModel.test.ts src/moduleEditor/diagramMetadata.test.ts`
- `rtk npm run test:unit -- src/diagramEditor/projectDiagram.test.ts src/diagramEditor/diagramImages.test.ts src/diagramEditor/sourceBackedSmokeModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/sourceBackedDiagramApplySmokeModel.test.ts src/moduleEditor/diagramMetadata.test.ts src/moduleEditor/ModuleEditor.test.tsx src/styles/diagram.test.ts`
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'focus_tree_preview_icons_resolve or focus_asset_component'`
- `rtk git diff --check`
- `rtk npm run build`
- Browser QA: `diagram-source-backed-smoke.html` and `diagram-apply-review-smoke.html` both render 9 focus images, 0 placeholders, and 34-unit image footprints inside the 48-unit grid.

## Risks Or Blockers

- Vite still reports the existing large-chunk warning.
- Full normal-app PIHC3 focus-tree interaction still needs broader usability work beyond the smoke pages.

## Next

- Continue moving the normal PIHC3 focus-tree tab toward the same source-backed, image-backed behavior verified by the smoke pages.
