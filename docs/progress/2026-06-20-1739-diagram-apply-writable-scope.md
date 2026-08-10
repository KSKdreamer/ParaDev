# Diagram Apply Writable Scope Progress

Date: 2026-06-20 17:39

Linear: TAL-000

## Done

- Disabled the diagram Apply action when the detailed dirty scope has affected entities but none of them has a writable metadata path.
- Added a warning message so users understand why a dirty PIHC3 diagram cannot be applied from the current scope.
- Kept Discard available for dirty diagrams so users can still clear local layout drafts.
- Gated the diagram save keyboard shortcut on the same writable-scope check.

## Verification

- Red check: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx` failed before implementation because Apply was still enabled.
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/diagramMetadata.test.ts src/moduleEditor/diagramSelection.test.ts src/moduleEditor/ModuleEditor.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke at `http://127.0.0.1:5173/`: app loaded, `科技` tab selected, no framework overlay, no warn/error console logs.

## Risks Or Blockers

- Plain Vite still shows the expected `SDK browser unavailable` placeholder because live SDK project data is provided by the Tauri shell.
- The production build still emits the existing Vite large chunk warning.

## Next

- Continue improving the diagram save/apply path so PIHC3 focus and technology edits explain exactly what metadata files will be written before users commit changes.
