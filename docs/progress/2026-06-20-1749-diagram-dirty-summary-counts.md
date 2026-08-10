# Diagram Dirty Summary Counts Progress

Date: 2026-06-20 17:49

Linear: TAL-000

## Done

- Added a PIHC3 diagram dirty-scope summary for mixed writable and skipped metadata rows.
- Kept the existing total-only summary when every dirty row has a writable path, so the common path stays compact.
- Added English and Chinese locale strings for the mixed writable/skipped metadata summary.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx` failed before implementation on the new mixed-summary expectation.
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor src/moduleEditor/diagramMetadata.test.ts src/moduleEditor/diagramSelection.test.ts src/moduleEditor/ModuleEditor.test.tsx src/moduleEditor/model.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke at `http://127.0.0.1:5173/`: app loaded with title `ParaDev`, the `科技` module click selected the Technology tab, and console warn/error logs were empty.

## Risks Or Blockers

- The plain Vite smoke still shows the expected `SDK browser unavailable` state because SDK browser data is only available in the Tauri shell.
- The build still reports the existing Vite large-chunk warning.

## Next

- Surface the same writable/skipped distinction in the selected draft panel or an Apply preview before committing metadata writes.
