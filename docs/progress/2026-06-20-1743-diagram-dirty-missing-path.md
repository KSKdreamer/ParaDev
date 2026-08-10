# Diagram Dirty Missing Path Progress

Date: 2026-06-20 17:43

Linear: TAL-000

## Done

- Labeled dirty metadata rows that do not have a writable metadata path in the diagram dirty scope.
- Kept mixed dirty scopes applyable when at least one affected entity still has a metadata path, while making skipped rows explicit.
- Added English and Chinese copy plus a warning-color row style for missing metadata paths.

## Verification

- Red check: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx` failed before implementation because missing-path rows had no label.
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/diagramMetadata.test.ts src/moduleEditor/diagramSelection.test.ts src/moduleEditor/ModuleEditor.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke at `http://127.0.0.1:5173/`: app loaded, `科技` tab selected, no framework overlay, no warn/error console logs.

## Risks Or Blockers

- Plain Vite still shows the expected `SDK browser unavailable` placeholder because live SDK project data is provided by the Tauri shell.
- The production build still emits the existing Vite large chunk warning.

## Next

- Continue improving the diagram apply preview so PIHC3 focus and technology edits can distinguish writable, skipped, and selected metadata changes before commit.
