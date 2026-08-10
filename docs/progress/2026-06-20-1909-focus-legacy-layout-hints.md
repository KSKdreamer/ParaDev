# 2026-06-20 19:09 - Focus Legacy Layout Hints

## Summary

- Added optional diagram node layout hints for PIHC/legacy focus positioning: `priority`, `subtreeWidth`, `subtreeWidthDelta`, and `subtreeCenterOffset`.
- Made auto layout pack children by descending priority, reserve subtree lane width, and apply center offsets while preserving existing auto-root placement.
- Made the focus diagram adapter preserve `priority`, `w/pw`, `dw`, `dc`, and partial `dx/dy` or `cx/cy` offsets from focus metadata.
- Preserved the new hint fields through diagram JSON import/export.

## Validation

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/layoutModel.test.ts src/diagramEditor/projectDiagram.test.ts src/diagramEditor/diagramJson.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run test:model`
- `rtk npm --prefix apps/desktop run build`

The Vite build still reports the existing large-chunk warning.

## Rendered Smoke

Opened `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html` in the in-app browser and confirmed:

- one SVG node image renders with a `data:image/png;base64,` href
- the node image has a visible browser bounding box
- document `scrollWidth` equals `clientWidth`
- diagram apply-review controls and node detail text render

Console output only had Vite connection debug lines and the React DevTools info line.
