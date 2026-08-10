# Diagram Relationship Scope Filter Progress

Date: 2026-06-20 17:18

Linear: TAL-000

## Done

- Tightened diagram relationship candidates from focus/non-focus filtering to source-scope filtering.
- Technology nodes now avoid focus-tree context candidates while keeping same-family technology candidates.
- Embedded focus nodes now avoid candidates from other focus-tree modules while keeping same focus-tree candidates.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/diagramMetadata.test.ts src/moduleEditor/diagramSelection.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke at `http://127.0.0.1:5173/`: app loaded, `科技` tab selected, no framework overlay, no warn/error console logs.

## Risks Or Blockers

- Plain Vite still shows the expected `SDK browser unavailable` placeholder because live SDK data requires the Tauri desktop shell.
- This pass hardens the rendered GUI candidate lists; JSON import and lower-level model guards should still be reviewed for the same source-scope rule.

## Next

- Extend the same source-scope rule into JSON import/model edit guards so pasted diagrams cannot create relationships the GUI no longer offers.
