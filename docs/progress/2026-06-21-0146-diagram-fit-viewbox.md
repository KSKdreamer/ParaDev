# Diagram Fit ViewBox Progress

Date: 2026-06-21 01:46

Linear: TAL-000

## Done

- Made the diagram canvas fit its base `viewBox` to the actual normal-window canvas aspect ratio instead of using only raw graph bounds.
- Kept the minimap and pan surface aligned with the same fitted coordinate space, so the visible viewport marker matches what the user sees.
- Preserved saved zoom and pan state on top of the fitted base view.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk git diff --check`
- Browser smoke on `http://127.0.0.1:5180/e2e/diagram-source-backed-smoke.html`: 6 focus nodes, 6 source-backed PNG preview icons, 0 legacy/default icons, max icon size 34 px, matching main/minimap fitted viewBox, no console warnings or errors.

## Risks Or Blockers

- This is still the current SVG-backed editor, not the eventual React Flow canvas from the design note.
- Large PIHC3 tree ergonomics still need continued browser-level tuning for first selection, minimap navigation, and toolbar density.

## Next

- Continue tuning large PIHC3 focus trees toward the grid-like HOI4 navigation model, especially branch selection and subtree movement feedback.
