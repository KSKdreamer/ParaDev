# Diagram Insert Affordance Progress

Date: 2026-06-20 17:04

Linear: n/a

## Done

- Hid child focus insertion controls when the selected node is not an embedded focus node.
- Hid root focus addition controls when the diagram has no embedded focus or focus-family context.
- Updated diagram view tests so non-focus/technology diagrams expect irrelevant focus insertion controls to be absent instead of disabled.

## Verification

- RED: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx` failed with the disabled insert controls still rendered for technology diagrams.
- GREEN: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx` - 90 passed.
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/diagramMetadata.test.ts src/moduleEditor/diagramSelection.test.ts` - 209 passed.
- `rtk npm --prefix apps/desktop run test:unit` - 334 passed.
- `rtk npm --prefix apps/desktop run build` - passed with the existing Vite large-chunk warning.
- Browser smoke at `http://127.0.0.1:5173/` loaded ParaDev, opened the PIHC3 technology tab, reported no framework overlay and no console warnings/errors. Plain Vite still shows the expected SDK-browser-unavailable placeholder.

## Risks Or Blockers

- Real SDK-backed diagram affordance validation still needs a Tauri/mocked-desktop-state path; component rendering tests cover the exact toolbar policy.

## Next

- Continue aligning relationship, parent, and insertion affordances with the layout/import guards so the GUI only offers valid PIHC3 diagram edits.
