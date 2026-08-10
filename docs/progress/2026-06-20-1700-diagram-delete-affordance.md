# Diagram Delete Affordance Progress

Date: 2026-06-20 17:00

Linear: n/a

## Done

- Hid focus deletion toolbar actions when the selected diagram node is not an embedded focus node.
- Added a regression covering source-backed non-focus nodes so PIHC3 technology/context nodes do not advertise focus removal commands.
- Updated existing removal affordance tests to expect hidden controls instead of disabled danger buttons for non-focus diagrams.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx` - 90 passed after RED/GREEN.
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/diagramMetadata.test.ts src/moduleEditor/diagramSelection.test.ts` - 209 passed.
- `rtk npm --prefix apps/desktop run test:unit` - 334 passed.
- `rtk npm --prefix apps/desktop run build` - passed with the existing Vite large-chunk warning.
- Browser smoke at `http://127.0.0.1:5173/` loaded ParaDev, opened the PIHC3 technology tab, and reported no console warnings/errors. Plain Vite still shows the expected SDK-browser-unavailable placeholder instead of real local SDK diagram data.

## Risks Or Blockers

- Real PIHC3 diagram rendering still needs Tauri or a mocked SDK browser state; this slice is covered by component-level rendering tests.

## Next

- Continue tightening focus/technology editor affordances so React never offers actions that the layout model rejects.
