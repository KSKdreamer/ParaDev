# 2026-06-21 10:45 - Diagram Image Status Tone

## Slice

- Made the diagram image hydration status pill distinguish loading, partial, and fully loaded states.
- Added a tooltip with checked/loaded counts so users can tell whether missing local focus/technology icons are still loading or failed hydration.
- Added English and Chinese strings for the detailed image-loading status.
- Left the PIHC3 nested `.git` directory untouched after confirming it is a real local clone with its own history and dirty state, not generated cache output.

## Verification

```bash
rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx src/styles/diagram.test.ts
rtk npm --prefix apps/desktop run build
rtk git diff --check -- apps/desktop/src/diagramEditor/ProjectDiagramView.tsx apps/desktop/src/diagramEditor/ProjectDiagramView.test.tsx apps/desktop/src/i18n/locales/en.ts apps/desktop/src/i18n/locales/zh.ts apps/desktop/src/styles/app.css
```

All commands passed. The production build still reports the existing large-chunk warning.
