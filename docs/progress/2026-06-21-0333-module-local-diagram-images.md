# Module Local Diagram Images Progress

Date: 2026-06-21 03:33

Linear: TAL-000

## Done

- Added diagram adapter support for module-local migrated image metadata such as `legacy_source_image.path: legacy/default.png`.
- Covered the PIHC3 technology module shape so `TECHNOLOGY_FIREARM_I` resolves to `src/modules/technology/TECHNOLOGY_FIREARM_I/legacy/default.png` when it has no explicit source-slot icon.
- Rechecked the focus-tree smoke canvas still uses PIHC3 `focus_asset_component/.../preview.png` images at 34 px, with no SVG placeholders.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/projectDiagram.test.ts src/diagramEditor/diagramImages.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx src/styles/diagram.test.ts`
- Browser smoke: `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html` reported 9 focus images, 0 placeholders, and 34 px focus image sizing.

## Risks Or Blockers

- Existing PIHC3 technology asset components still do not all have generated `preview.png` files; the GUI now uses the migrated module-local legacy source image where present.

## Next

- Add technology asset-component preview generation if the PIHC3 technology tree should prefer compiled `technology_asset_component` previews over module-local legacy source images.
