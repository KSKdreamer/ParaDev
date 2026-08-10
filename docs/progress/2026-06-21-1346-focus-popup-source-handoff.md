# Focus Popup Source Handoff Progress

Date: 2026-06-21 13:46

Linear: TAL-000

## Done

- Added derived source slots for PIHC source-backed focus `legacy/<focus>/info.json` files when focus-tree metadata exposes `source_focuses` records.
- Extended the diagram popup module-jump handoff to carry the selected focus source path into the normal module editor.
- Updated module details so an external source path opens the matching source tab directly, letting the popup jump land on the selected focus `info.json` editor instead of only the backing focus tree.

## Verification

- Red tests first: `rtk npm --prefix apps/desktop exec vitest run src/moduleEditor/model.test.ts src/moduleEditor/ModuleEntityDetails.test.tsx src/moduleEditor/ModuleEditor.test.tsx` failed on missing PIHC focus info slots, ignored target source paths, and default entity selection.
- `rtk npm --prefix apps/desktop exec vitest run src/moduleEditor/model.test.ts src/moduleEditor/ModuleEntityDetails.test.tsx src/moduleEditor/ModuleEditor.test.tsx`
- `rtk npm --prefix apps/desktop exec vitest run e2e/diagram-tab-smoke-state.test.ts e2e/source-backed-focus-image-bridge.test.ts src/diagramEditor/sourceBackedSmokeModel.test.ts src/moduleEditor/sourceBackedDiagramApplySmokeModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/ModuleEditor.test.tsx src/moduleEditor/ModuleEntityDetails.test.tsx src/moduleEditor/model.test.ts src/components/Workspace.test.tsx src/components/AppShell.test.tsx src/App.test.ts src/styles/diagram.test.ts`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke at `http://127.0.0.1:5180/e2e/diagram-tab-smoke.html`: opened `FOCUS_C01_DEM_CHANGE`, clicked `Open module item`, and verified the normal `National Focuses` tab selected `C01 Main` with `FOCUS_C01_DEM_CHANGE info` active in a source editor panel and no console warnings/errors.

## Risks Or Blockers

- Large focus trees now expose many focus info source tabs in the normal module editor; this is functional, but the tab strip will need grouping/search if users edit many focus files in one session.
- The production build still emits the existing Vite large-chunk warning.

## Next

- Improve the normal module editor source-tab ergonomics for large PIHC focus trees while preserving the direct focus-node handoff.
