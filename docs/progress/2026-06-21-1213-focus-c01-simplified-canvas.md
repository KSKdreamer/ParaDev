# Focus C01 Simplified Canvas Progress

Date: 2026-06-21 12:13

Linear: TAL-000

## Done

- Kept focus-tree diagram tabs separate from normal module tabs while opening C01_MAIN as a full, fitted HOI4-style focus tree.
- Changed unsaved focus-tree diagrams to open at the fitted 100% viewport instead of the previous automatic 200% inspect zoom, while saved viewport zoom still restores.
- Preserved high-DPI focus icons by hydrating 2x source PNGs into 72 px SVG images on the 96 px focus-coordinate grid; visible grid lines remain 48 px half-cells.
- Added per-node SVG hover panels for read-only focus details and a selected-node relative/pin/auto mode switch on focus icons.
- Simplified the focus-tree canvas chrome by hiding the old selected-node inspector, advanced JSON/layout toolbar groups, node-tool row, and pan button cluster for focus-tree diagrams.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx src/styles/diagram.test.ts src/moduleEditor/ModuleEditor.test.tsx`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke at `http://127.0.0.1:5180/e2e/diagram-tab-smoke.html`: opened National Focuses diagram, confirmed C01_MAIN shows 83 nodes, 83 hydrated images, 0 placeholders, 0 arrow markers, 0 focus-title plaques, fitted 100% zoom, hidden inspector/advanced groups, and no console warnings/errors.
- Browser interaction smoke: double-clicked `FOCUS_C01_COZY_GLOW_CORONATION` and confirmed it selected; clicked its selected-node mode switch and confirmed it cycled from auto to relative in app state.

## Risks Or Blockers

- The hover panel is covered by unit/CSS tests and exists hidden at rest in browser smoke, but the in-app browser CUA move API did not toggle CSS `:hover`, so rendered hover opacity was not browser-verified.
- Double-click currently selects/opens the embedded focus node within the diagram surface; full module-tab jump or pop-up focus detail still needs a workspace-level route.
