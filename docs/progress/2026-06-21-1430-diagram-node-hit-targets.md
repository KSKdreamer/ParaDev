# Diagram Node Hit Targets Progress

Date: 2026-06-21 14:30

Linear: TAL-000

## Done

- Added a dedicated `.project-diagram-node-hit-target` rect with `data-node-hit-id` for each diagram node.
- Kept decorative focus/technology icon frames out of pointer hit testing so the transparent node hit rect remains the stable interaction surface.
- Preserved the existing icon-first visual style while giving browser smoke tests and future interaction tooling a precise node target.

## Verification

- Red test first: `rtk npm --prefix apps/desktop exec vitest run src/diagramEditor/ProjectDiagramView.test.tsx src/styles/diagram.test.ts` failed because the hit-target markup and CSS block were missing.
- `rtk npm --prefix apps/desktop exec vitest run src/diagramEditor/ProjectDiagramView.test.tsx src/styles/diagram.test.ts`
- `rtk npm --prefix apps/desktop exec vitest run src/diagramEditor/ProjectDiagramView.test.tsx src/styles/diagram.test.ts e2e/diagram-tab-smoke-state.test.ts src/moduleEditor/ModuleEditor.test.tsx src/moduleEditor/ModuleEntityDetails.test.tsx`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke at `http://127.0.0.1:5180/e2e/diagram-tab-smoke.html`: opened the National Focuses diagram, confirmed 83 C01 hit targets for 83 C01 nodes, double-clicked `data-node-hit-id="FOCUS_C01_DEM_CHANGE"`, and confirmed the popup source path `src/modules/focus_tree/C01_MAIN/legacy/C01_DEM_CHANGE/info.json` with no console warnings/errors.

## Risks Or Blockers

- The production build still emits the existing Vite large-chunk warning.

## Next

- Use the stable node hit target in browser smoke flows that exercise popup-to-module source handoff end to end.
