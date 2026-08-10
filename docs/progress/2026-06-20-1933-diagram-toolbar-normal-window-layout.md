# 2026-06-20 19:33 - Diagram Toolbar Normal Window Layout

## Summary

- Split the diagram editor header into a summary row and grouped toolbar controls so search, viewport, file/history, layout, status, and selected-node tools no longer compete in one long flex line.
- Moved selected-node nudge/layout/remove controls into a full-width horizontally scrollable group.
- Added stable canvas minimum heights so the focus tree remains usable in normal Tauri/browser windows instead of collapsing under toolbar wrapping.
- Added a responsive shorter-window rule so the selected-node summary can scroll without covering the canvas.

## Validation

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke page at `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html?toolbar-groups=1`
  - `1440x900`: header 127px, canvas 689px, no horizontal overflow.
  - `1024x768`: header 158px, canvas 526px, no horizontal overflow.

The Vite build still reports the existing large-chunk warning.
