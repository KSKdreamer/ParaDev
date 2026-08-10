# Diagram Empty Candidate Forms Progress

Date: 2026-06-20 17:14

Linear: TAL-000

## Done

- Hid selected-node parent, prerequisite, and reference edit forms when the selected diagram node has no valid same-kind candidates.
- Kept valid edit forms visible when a same-kind peer exists, including the prerequisite form regression fixture.
- Added regression coverage for embedded focus nodes whose only peer is a non-focus focus-tree context node.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/diagramMetadata.test.ts src/moduleEditor/diagramSelection.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke at `http://127.0.0.1:5173/`: app loaded, `科技` tab selected, no framework overlay, no warn/error console logs.

## Risks Or Blockers

- Plain Vite still shows the expected `SDK browser unavailable` placeholder because live SDK data requires the Tauri desktop shell.
- `apps/desktop/src/diagramEditor/` remains untracked as part of the broader diagram editor work, so normal `git diff` does not show these edits yet.

## Next

- Continue trimming invalid inspector actions and metadata write paths so PIHC3 focus/technology diagrams only expose operations the SDK can persist.
