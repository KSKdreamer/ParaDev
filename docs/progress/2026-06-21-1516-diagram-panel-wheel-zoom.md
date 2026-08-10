# 2026-06-21 Diagram Panel Wheel Zoom

## Scope

- Extended the existing Ctrl/Command + mouse wheel diagram zoom listener from the canvas wrapper to the whole diagram panel, so toolbar/header and canvas-region wheel gestures share the same viewport zoom behavior.
- Added an SVG-bounds guard for cursor anchoring. Wheel gestures that start over the actual SVG stay cursor-anchored; gestures from panel UI outside the SVG keep the current pan instead of anchoring to an off-canvas point.
- Marked the panel with `data-diagram-wheel-zoom-surface="panel"` for smoke/debug confirmation.

## Verification

- Red test first: `rtk npm --prefix apps/desktop exec vitest run src/diagramEditor/ProjectDiagramView.test.tsx` failed on the missing panel marker and missing SVG-bounds helper.
- Green focused test: `rtk npm --prefix apps/desktop exec vitest run src/diagramEditor/ProjectDiagramView.test.tsx`
- Nearby regression run: `rtk npm --prefix apps/desktop exec vitest run src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/layoutModel.test.ts src/diagramEditor/diagramHistory.test.ts src/moduleEditor/ModuleEditor.test.tsx src/styles/diagram.test.ts e2e/diagram-tab-smoke-state.test.ts`
- Build: `rtk npm --prefix apps/desktop run build` passed with the existing Vite chunk-size warning.
- Rendered smoke: `http://127.0.0.1:5180/e2e/diagram-tab-smoke.html`, opened `National Focuses diagram`, verified `panelMarker: "panel"`, `C01` nodes present, and no console errors/warnings.
- Interaction proof via Playwright fallback: Ctrl-wheel over canvas changed zoom `100% -> 150%`; Ctrl-wheel over the diagram toolbar changed zoom `150% -> 200%`; `window.visualViewport.scale` stayed `1`.

## Notes

- Browser CUA `scroll(..., keypress: ["Control"])` did not synthesize a `ctrlKey` wheel event in this environment, so the final modifier-wheel interaction proof used the Playwright fallback attached to the same smoke URL.
