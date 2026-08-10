# Focus Source Backed Fixture Progress

Date: 2026-06-21 01:05

Linear: TAL-000

## Done

- Added a larger C08_MAIN diagram adapter fixture based on real PIHC3 focus-tree metadata.
- The fixture covers six source-backed focus nodes with `source_focuses.icon_path`, compiled focus positions/prerequisites, compact 2 x 2 node sizing, migrated `focus_asset_component/.../preview.png` images, and tree/dependency edges.
- The test explicitly rejects legacy `default.png` canvas image URLs for these source-backed focus nodes.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/projectDiagram.test.ts -t "larger PIHC3 source-backed"`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/projectDiagram.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/diagramImages.test.ts src/diagramEditor/layoutModel.test.ts src/styles/diagram.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`

## Risks Or Blockers

- This is a test fixture copied from PIHC3 metadata, not a dynamic YAML reader in the desktop test runtime.
- Vite build still reports the existing large-chunk warning.

## Next

- Add a real browser smoke path for a source-backed project-browser payload when the GUI can cheaply load a larger PIHC3 tree without hand-built fixture data.
