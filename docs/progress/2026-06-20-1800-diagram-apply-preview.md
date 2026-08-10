# Diagram Apply Preview Progress

Date: 2026-06-20 18:00

Linear: TAL-000

## Done

- Added a compact diagram Apply preview for path-aware PIHC3 metadata drafts that include skipped rows.
- The preview uses `DiagramChangedEntity.path` to show writable versus skipped counts, for example `Will write 1 · Skip 1`.
- Kept legacy id-only dirty state out of the preview so the GUI does not infer skipped writes when metadata paths are unknown.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx` failed before implementation on the new Apply-preview expectation.
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor src/moduleEditor/diagramMetadata.test.ts src/moduleEditor/diagramSelection.test.ts src/moduleEditor/ModuleEditor.test.tsx src/moduleEditor/model.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke at `http://127.0.0.1:5173/`: app loaded with title `ParaDev`, the `科技` module click selected the Technology tab, and console warn/error logs were empty.

## Risks Or Blockers

- Plain Vite still shows the expected `SDK browser unavailable` state; SDK-backed project browser data needs Tauri.
- The build still reports the existing Vite large-chunk warning.

## Next

- Wire the same writable/skipped apply preview into a fuller confirmation or review surface before diagram metadata writes.
