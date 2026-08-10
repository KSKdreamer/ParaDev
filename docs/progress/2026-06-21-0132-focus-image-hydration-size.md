# Focus Image Hydration Size Progress

Date: 2026-06-21 01:32

Linear: TAL-000

## Done

- Wired diagram image hydration to use a per-node thumbnail side length, so compact focus nodes cache and render migrated PIHC3 `preview.png` images at the same size as the SVG icon.
- Kept 2 x 2 focus nodes as compact icon tiles: the rendered preview image is 34 x 34 inside a 48 x 48 grid footprint.
- Verified the source-backed C08_MAIN smoke page renders actual PNG data images from `src/modules/focus_asset_component/.../preview.png` with no legacy/default focus image paths.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramImages.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/projectDiagram.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk bash scripts/test.bash tests/test_pihc3_migration_contracts.py -k focus_tree_preview_icons_resolve -q`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke at `http://127.0.0.1:5180/e2e/diagram-source-backed-smoke.html`: 6 focus nodes, 6 hydrated PNG images, 0 placeholders, max icon size 34 x 34, no console warnings/errors.

## Risks Or Blockers

- The broader focus-tree editor still needs more large-tree UX work; this checkpoint only hardens migrated image loading and compact icon sizing.

## Next

- Continue improving normal-window focus tree ergonomics and larger PIHC3 tree navigation.
