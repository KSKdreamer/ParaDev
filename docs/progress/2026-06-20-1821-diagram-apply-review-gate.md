# Diagram Apply Review Gate Progress

Date: 2026-06-20 18:21

Linear: TAL-000

## Done

- Added a two-step Apply gate for mixed PIHC3 diagram metadata drafts.
- When the diagram has both writable and skipped metadata rows, the first Apply action now says `Review scope first` and only accepts the visible review scope.
- After review acceptance, the same action can call the existing diagram Apply bridge for writable rows.
- Kept normal all-writable diagram applies as one-click `Apply diagram`.
- Kept the SDK/Tauri write path unchanged.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx` failed before implementation because the mixed Apply button did not render `Review scope first`.
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor src/moduleEditor/diagramMetadata.test.ts src/moduleEditor/diagramSelection.test.ts src/moduleEditor/ModuleEditor.test.tsx src/moduleEditor/model.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke at `http://127.0.0.1:5173/`: app loaded with title `ParaDev`, the `科技` module click selected the Technology tab, no framework overlay appeared, and console warn/error logs were empty.

## Risks Or Blockers

- Plain Vite still shows `SDK browser unavailable`; SDK-backed dirty diagram review needs the Tauri shell or a mocked rendered harness.
- The build still reports the existing Vite large-chunk warning.

## Next

- Add a rendered dirty-diagram harness so the mixed Apply review gate can be clicked end-to-end without requiring a full Tauri session.
