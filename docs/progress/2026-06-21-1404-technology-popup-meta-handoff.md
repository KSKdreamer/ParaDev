# Technology Popup Meta Handoff Progress

Date: 2026-06-21 14:04

Linear: TAL-000

## Done

- Added technology-node popup source-path parity with focus nodes: opened technology diagram nodes now show `src/modules/technology/<id>/meta.yaml` when the node payload has a module-relative root.
- Kept focus-node popup behavior on source-backed `legacy/<focus>/info.json`.
- Exposed reported `meta` sources as normal source tabs in the module editor, so opening from a technology diagram can land directly on `meta.yaml` instead of only selecting the module row.

## Verification

- Red tests first: `rtk npm --prefix apps/desktop exec vitest run src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/ModuleEditor.test.tsx` failed because technology popups did not show `meta.yaml` and the module editor hid the `meta` source tab.
- `rtk npm --prefix apps/desktop exec vitest run src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/ModuleEditor.test.tsx src/moduleEditor/ModuleEntityDetails.test.tsx`
- `rtk npm --prefix apps/desktop exec vitest run e2e/diagram-tab-smoke-state.test.ts e2e/source-backed-focus-image-bridge.test.ts src/diagramEditor/sourceBackedSmokeModel.test.ts src/moduleEditor/sourceBackedDiagramApplySmokeModel.test.ts src/moduleEditor/technologyDiagramApplySmokeModel.test.ts src/diagramEditor/projectDiagram.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/ModuleEditor.test.tsx src/moduleEditor/ModuleEntityDetails.test.tsx src/components/Workspace.test.tsx src/components/AppShell.test.tsx src/styles/diagram.test.ts`
- `rtk npm --prefix apps/desktop run build`

## Risks Or Blockers

- This slice verifies rendered React markup and source-tab selection; it did not run a fresh browser gesture smoke.
- The production build still emits the existing Vite large-chunk warning.
