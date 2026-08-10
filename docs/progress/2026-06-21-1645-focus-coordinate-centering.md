# 2026-06-21 16:45 Focus Coordinate Centering

## Summary

- Kept rendered focus icons and hit targets centered on their PIHC/HOI4 `x,y` coordinate by using the centered 1.5-slot visible footprint.
- Extended viewport centering helpers so search, selected-footprint centering, and related navigation use the same visible focus footprint instead of treating `x,y` as the upper-left corner.

## Verification

```bash
rtk npm --prefix apps/desktop exec vitest run src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts
rtk npm --prefix apps/desktop run build
```

Browser smoke:

- `http://127.0.0.1:5180/e2e/diagram-tab-smoke.html`
- Opened `National Focuses diagram`.
- Verified `FOCUS_C01_DEM_CHANGE` renders a `72 x 72` focus image and hit target at `x=-36, y=-36` inside the node transform, so the coordinate is the icon center.
- Verified no new browser console warnings/errors after reload.
