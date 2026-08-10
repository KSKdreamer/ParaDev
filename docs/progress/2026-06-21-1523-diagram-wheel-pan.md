# 2026-06-21 Diagram Wheel Pan

## Scope

- Added normal mouse-wheel panning for the rendered diagram SVG, scaled from screen deltas into current viewBox units.
- Kept Ctrl/Command + wheel as zoom, and kept ordinary panel chrome outside the SVG from being captured for wheel pan.
- Added Shift + wheel horizontal panning for wide HOI4-style focus trees.

## Verification

- Red test first: `rtk npm --prefix apps/desktop exec vitest run src/diagramEditor/ProjectDiagramView.test.tsx` failed on missing `diagramWheelPanDelta`.
- Green focused test: `rtk npm --prefix apps/desktop exec vitest run src/diagramEditor/ProjectDiagramView.test.tsx`
- Nearby regression run: `rtk npm --prefix apps/desktop exec vitest run src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/layoutModel.test.ts src/diagramEditor/diagramHistory.test.ts src/moduleEditor/ModuleEditor.test.tsx src/styles/diagram.test.ts e2e/diagram-tab-smoke-state.test.ts`
- Build: `rtk npm --prefix apps/desktop run build` passed with the existing Vite chunk-size warning.
- Rendered smoke: `http://127.0.0.1:5180/e2e/diagram-tab-smoke.html`, opened `National Focuses diagram`, verified 83 C01 nodes and no console warnings/errors.
- Interaction proof: regular wheel over the SVG changed only viewBox Y while page scroll stayed `0`; Shift + wheel changed only viewBox X; Ctrl + wheel still zoomed from `100%` to `150%`.

## Notes

- Browser CUA verified regular wheel panning. Its scroll API did not synthesize the Shift modifier, so the Shift-wheel and Ctrl-wheel interaction proof used the Playwright fallback on the same smoke URL.
