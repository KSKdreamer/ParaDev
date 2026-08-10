# Diagram Ctrl Wheel Zoom Progress

Date: 2026-06-21 13:16

Linear: TAL-000

## Done

- Added Ctrl + mouse wheel zoom handling to `ProjectDiagramView`, using the same discrete zoom levels and viewport persistence path as the existing toolbar and keyboard zoom controls.
- Confirmed the prior zoom features were toolbar buttons plus keyboard `+`/`-`; there was no existing wheel handler.

## Verification

- Red test first: `rtk npm --prefix apps/desktop exec vitest run src/diagramEditor/ProjectDiagramView.test.tsx` failed because `diagramWheelZoomDelta` did not exist.
- `rtk npm --prefix apps/desktop exec vitest run src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop exec vitest run e2e/diagram-tab-smoke-state.test.ts e2e/source-backed-focus-image-bridge.test.ts src/diagramEditor/sourceBackedSmokeModel.test.ts src/moduleEditor/sourceBackedDiagramApplySmokeModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/styles/diagram.test.ts`
- `rtk npm --prefix apps/desktop run build`
- Browser health check at `http://127.0.0.1:5180/e2e/diagram-tab-smoke.html`: page title `ParaDev Diagram Tab Smoke`, DOM contains the focus diagram, console warnings/errors empty, selected diagram tab shows C01_MAIN with 83 focus images and `Images 83/83`.

## Risks Or Blockers

- The in-app CUA scroll API did not synthesize a Ctrl-modified wheel event, so the exact modifier-wheel interaction is unit-covered and wired in React but not directly browser-driven in this session.
- The production build still emits the existing Vite large-chunk warning.
