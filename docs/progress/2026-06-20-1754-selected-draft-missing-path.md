# Selected Draft Missing Path Progress

Date: 2026-06-20 17:54

Linear: TAL-000

## Done

- Added selected-node draft feedback for PIHC3 diagram metadata rows that have no writable metadata path.
- Reused the existing missing-path translation so the selected draft pill, dirty list, and Apply-disabled warning stay consistent.
- Added scoped styling so the missing-path line is warning-colored inside the selected draft pill.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx` failed before implementation on the new selected-draft missing-path expectation.
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor src/moduleEditor/diagramMetadata.test.ts src/moduleEditor/diagramSelection.test.ts src/moduleEditor/ModuleEditor.test.tsx src/moduleEditor/model.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke at `http://127.0.0.1:5173/`: app loaded with title `ParaDev`, the `科技` module click selected the Technology tab, and console warn/error logs were empty.

## Risks Or Blockers

- Plain Vite still shows the expected `SDK browser unavailable` state; SDK-backed project browser data needs Tauri.
- The build still reports the existing Vite large-chunk warning.

## Next

- Add an Apply preview that separates writable metadata rows from skipped metadata rows before the user writes diagram changes.
