# Source Backed C08 Part IV Images Progress

Date: 2026-06-21 06:37

Linear: TAL-000

## Done

- Added a shared source-backed C08_PARTIV diagram smoke model that builds the real `ProjectDiagramView` document from PIHC3 project-browser metadata, including source `parent: null` roots, `dx`, `x`, `y`, and `priority` layout hints.
- Migrated `diagram-source-backed-smoke.html` from the old inline C08_MAIN six-node sample to the C08_PARTIV model and imported all nine migrated `focus_asset_component/.../preview.png` images.
- Updated the source-backed E2E fixture contract to assert two independent source roots, 9 rendered focus images, 20 graph edges, and no legacy `default.png` image fallback.

## Verification

- `rtk npm run test:unit -- src/diagramEditor/sourceBackedSmokeModel.test.ts src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/styles/diagram.test.ts`
- `rtk npm run build`
- Browser smoke at `http://127.0.0.1:5180/e2e/diagram-source-backed-smoke.html`: 9 `.project-diagram-node-image.focus-icon` images, 0 placeholders, 9 bridge reads, 9 cache writes, `data-paradev-source-backed-root-count="2"`, and every image rendered at 34 x 34 px inside a 48 px focus slot.

## Risks Or Blockers

- None for this slice. The full focus-tree editor still needs broader editing ergonomics and richer subtree layout controls.

## Next

- Continue moving rendered focus-tree behavior from fixtures into the normal GUI path, especially drag/apply flows for source-backed PIHC3 focus layout fields.
