# Focus Node Info Popup Progress

Date: 2026-06-21 12:40

## Done

- Added a controlled focus-node info popup for double-clicked diagram nodes, including focus name, grid coordinates, diagram facts, and source-backed `legacy/<focus>/info.json` path.
- Wired the module editor to open the popup on node double-click and clear stale popup state when the focus-tree scope or selected module changes.
- Fixed SVG node hit-testing so transparent compact focus slots receive clicks above the canvas pan surface.

## Verification

- `rtk npm --prefix apps/desktop exec vitest run src/diagramEditor/ProjectDiagramView.test.tsx src/styles/diagram.test.ts`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke at `http://127.0.0.1:5180/e2e/diagram-tab-smoke.html`: opened the separate National Focuses diagram tab, confirmed C01_MAIN with 83/83 hydrated data URL focus images and zero placeholders, then double-clicked `FOCUS_C01_DEM_CHANGE` to open the read-only popup with `src/modules/focus_tree/C01_MAIN/legacy/C01_DEM_CHANGE/info.json`.

## Next

- Keep reducing remaining focus-tree toolbar noise and add a direct smoke contract for double-click popup state if the browser fixture grows an interaction harness.
