# 2026-06-20 18:57 - Focus Node Image Hydration

## Summary

- Made PIHC3 focus diagram nodes prefer `source_focuses.icon_path` legacy PNGs for browser-renderable node images.
- Kept compiled focus asset DDS paths as a fallback when a focus only has a `GFX_FOCUS_*_icon` key.
- Added a diagram thumbnail transform so local project images are decoded, cropped to a square thumbnail, cached as PNG, and not cached as broken raw image bytes.
- Extended the diagram apply-review smoke fixture with a mocked Tauri binary-source bridge and a local focus icon path.

## Validation

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/projectDiagram.test.ts src/diagramEditor/diagramImages.test.ts`
- `rtk npm --prefix apps/desktop run test:model`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`

The Vite build still reports the existing large-chunk warning.

## Rendered Smoke

Opened `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html` at `1440x900` and confirmed:

- `imageCount = 1`
- SVG image href starts with `data:image/png;base64,`
- `data-paradev-diagram-image-read-count = 1`
- `data-paradev-diagram-image-cache-write-count = 1`
- last image path is `src/modules/focus_asset_component/FOCUS_ASSET_COMPONENT_C08_PARTIV/legacy/focuses/C08_PARTIV/default.png`
- document `scrollWidth` equals `clientWidth`

Console output only had the React DevTools info line.
