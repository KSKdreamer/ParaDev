# 2026-06-20 18:50 - Focus Diagram Tab Layout

## Summary

- Split project diagrams out of the normal module editor surface by adding dedicated `diagram:*` workspace tabs for focus trees and technologies.
- Kept normal module tabs as plain entity list/details editors with no embedded diagram panel.
- Routed focus/technology module selection to the dedicated diagram tab, labeled as `{module}图谱` / `{module} diagram`.
- Added PIHC3 focus icon path inference from focus metadata, including `GFX_FOCUS_*_icon` keys mapped to `src/modules/focus_asset_component/.../gfx/interface/goals/*.dds`.
- Added legacy focus offset support: `parent` + `dx/dy` or `cx/cy` becomes relative diagram positioning, while root `x/y` remains absolute.
- Tightened diagram toolbar wrapping so normal-width windows do not reproduce the previous one-line toolbar overflow.

## Validation

- `rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts src/moduleEditor/ModuleEditor.test.tsx src/diagramEditor/projectDiagram.test.ts`
- `rtk npm --prefix apps/desktop run test:model`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`

The Vite build still reports the existing large-chunk warning.

## Rendered Smoke

- Opened `http://127.0.0.1:5180/` at `1440x900`, selected `国策`, and confirmed the selected workspace tab is `国策图谱` with no `.module-editor-grid` in the tab content.
- Opened `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html` at `1440x900`, confirmed the real diagram toolbar wraps without horizontal document overflow and the canvas remains visible.

Plain Vite cannot load the Tauri SDK browser payload, so the real PIHC3 data-backed diagram rendering remains covered by the adapter/model tests in this slice.
