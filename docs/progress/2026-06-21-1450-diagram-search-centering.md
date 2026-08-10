# Diagram Search Centering Progress

Date: 2026-06-21 14:50

Linear: TAL-000

## Done

- Center the first matching diagram node as soon as the node search query changes.
- Select the matching node during search entry so the focused C01 icon, hit target, and mode chip stay in sync.
- Reuse the clamped zoom-step helper for keyboard zoom shortcuts so canvas zoom controls share the same boundary behavior.

## Verification

- Red: `rtk npm --prefix apps/desktop exec vitest run src/diagramEditor/ProjectDiagramView.test.tsx` failed before `diagramSearchViewportTarget` existed.
- Green: `rtk npm --prefix apps/desktop exec vitest run src/diagramEditor/ProjectDiagramView.test.tsx`.
- Green: `rtk npm --prefix apps/desktop exec vitest run src/diagramEditor/ProjectDiagramView.test.tsx src/styles/diagram.test.ts e2e/diagram-tab-smoke-state.test.ts`.
- Green: `rtk npm --prefix apps/desktop run build` with the existing Vite large-chunk warning.
- Browser smoke: `http://127.0.0.1:5180/e2e/diagram-tab-smoke.html` opened the National Focuses diagram, rendered C01 Main with 83 nodes and 83 images, searched `FOCUS_C01_DEM_CHANGE`, selected and centered that node, and reported no console warnings or errors.

## Risks Or Blockers

- Browser automation still verifies the resulting canvas state rather than synthesizing every physical Ctrl/Command-wheel path.

## Next

- Continue tightening diagram navigation around large focus trees: search-result stepping, minimap interaction, and predictable saved viewport restore.
