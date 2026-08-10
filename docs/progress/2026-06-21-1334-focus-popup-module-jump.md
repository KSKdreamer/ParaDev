# Focus Popup Module Jump Progress

Date: 2026-06-21 13:34

Linear: TAL-000

## Done

- Added an `Open module item` action to the opened diagram-node info popover when the app can map the node back to a normal module editor item.
- Wired the action from `ProjectDiagramView` through `ModuleEditor`, `Workspace`, `AppShell`, and `App` so a focus-tree node in the diagram tab can open the normal module tab with its backing focus tree selected.
- Updated the diagram-tab smoke fixture to expose and exercise the same module-jump handoff.

## Verification

- Red test first: `rtk npm --prefix apps/desktop exec vitest run src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/ModuleEditor.test.tsx` failed because the popup did not render `Open module item`.
- `rtk npm --prefix apps/desktop exec vitest run src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/ModuleEditor.test.tsx src/components/Workspace.test.tsx src/components/AppShell.test.tsx src/App.test.ts`
- `rtk npm --prefix apps/desktop exec vitest run e2e/diagram-tab-smoke-state.test.ts e2e/source-backed-focus-image-bridge.test.ts src/diagramEditor/sourceBackedSmokeModel.test.ts src/moduleEditor/sourceBackedDiagramApplySmokeModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/ModuleEditor.test.tsx src/components/Workspace.test.tsx src/components/AppShell.test.tsx src/App.test.ts src/styles/diagram.test.ts`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke at `http://127.0.0.1:5180/e2e/diagram-tab-smoke.html`: opened `FOCUS_C01_DEM_CHANGE`, saw `Open module item`, clicked it, and verified the active tab changed from `National Focuses diagram` to `National Focuses` with `C01 Main` selected and no console warnings/errors.

## Risks Or Blockers

- The jump selects the backing focus tree module (`C01 Main`) because embedded focus nodes are stored inside a focus-tree module; per-focus editing still relies on the module detail/source editor surfaces.
- The production build still emits the existing Vite large-chunk warning.

## Next

- Continue reducing friction between focus-node inspection and source/detail editing, especially per-focus source-slot visibility in the normal module editor.
