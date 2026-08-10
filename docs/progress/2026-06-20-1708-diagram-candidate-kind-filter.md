# Diagram Candidate Kind Filter Progress

Date: 2026-06-20 17:08

Linear: n/a

## Done

- Made diagram relationship and parent candidate filtering symmetric: embedded focus nodes only offer embedded focus candidates, and non-focus nodes only offer non-focus candidates.
- Added a PIHC3-style regression for a selected technology node beside an embedded focus node and another technology peer.
- Confirmed parent, prerequisite, and reference quick candidates keep the valid technology peer and drop the embedded focus endpoint.

## Verification

- RED: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx` failed because `FOCUS_NEW_ROOT` still appeared as a parent/prerequisite/reference candidate for a technology node.
- GREEN: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx` - 91 passed.
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/diagramMetadata.test.ts src/moduleEditor/diagramSelection.test.ts` - 210 passed.
- `rtk npm --prefix apps/desktop run test:unit` - 335 passed.
- `rtk npm --prefix apps/desktop run build` - passed with the existing Vite large-chunk warning.
- Browser smoke at `http://127.0.0.1:5173/` loaded ParaDev, opened the PIHC3 technology tab, reported no framework overlay and no console warnings/errors. Plain Vite still shows the expected SDK-browser-unavailable placeholder.

## Risks Or Blockers

- Plain Vite cannot render real SDK-backed PIHC3 diagram data; component rendering tests cover the exact candidate policy.

## Next

- Continue aligning inspector edit forms and existing relationship displays with layout/import guards so users only see valid graph-edit actions.
