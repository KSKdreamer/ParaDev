# Diagram Canvas Wheel Capture Progress

Date: 2026-06-21 13:57

Linear: TAL-000

## Done

- Moved diagram Ctrl/Command + mouse wheel zoom interception from the SVG React wheel handler to a native non-passive wheel listener on the diagram canvas container.
- Kept normal mouse wheel scrolling untouched when neither Ctrl nor Command is held.
- Reused the existing discrete diagram zoom levels, cursor anchoring helper, and viewport persistence path.
- Added Command-scroll recognition alongside Ctrl-scroll so macOS modifier-wheel input follows the same zoom path.

## Verification

- Red test first: `rtk npm --prefix apps/desktop exec vitest run src/diagramEditor/ProjectDiagramView.test.tsx` failed because Command-scroll mapped to no zoom delta.
- `rtk npm --prefix apps/desktop exec vitest run src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop exec vitest run e2e/diagram-tab-smoke-state.test.ts e2e/source-backed-focus-image-bridge.test.ts src/diagramEditor/sourceBackedSmokeModel.test.ts src/moduleEditor/sourceBackedDiagramApplySmokeModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/styles/diagram.test.ts src/components/Workspace.test.tsx src/components/AppShell.test.tsx`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke at `http://127.0.0.1:5180/e2e/diagram-tab-smoke.html`: opened the National Focuses diagram, confirmed the diagram canvas rendered at `100%`, and console warnings/errors were empty.

## Risks Or Blockers

- The in-app browser scroll API still did not synthesize a Ctrl/Command-modified wheel event in this session, so the exact native gesture is covered by unit/type/build verification rather than browser automation.
- The production build still emits the existing Vite large-chunk warning.
