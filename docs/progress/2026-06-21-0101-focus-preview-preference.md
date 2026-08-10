# Focus Preview Preference Progress

Date: 2026-06-21 01:01

Linear: TAL-000

## Done

- Changed project-browser focus diagram image selection so source-backed focus nodes prefer migrated `focus_asset_component/.../preview.png` images over PIHC2 `legacy/focuses/.../default.png` paths.
- Kept explicit direct image URLs highest priority and retained legacy source images as a fallback.
- Updated adapter tests so source metadata still drives layout while migrated previews drive canvas imagery.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/projectDiagram.test.ts -t "migrated PIHC3 focus previews|source focus layout"`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/projectDiagram.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/diagramImages.test.ts src/diagramEditor/layoutModel.test.ts src/styles/diagram.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- In-app browser smoke at `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html`: 9 focus images, 9 migrated preview images, 0 legacy default images, 0 placeholders, max SVG icon size 34 px, no horizontal overflow.

## Risks Or Blockers

- The full PIHC3 browser tab should still be checked against a larger real tree, not only the focused adapter tests and representative smoke fixture.
- Vite build still reports the existing large-chunk warning.

## Next

- Add a larger project-browser focus-tree fixture or smoke path that exercises real `source_focuses` metadata from PIHC3 with migrated preview images.
