# 2026-06-20 11:25 - Selected Diagram Draft Marker

## Scope

Improved the desktop focus/technology diagram editor context panel so a selected node now shows when its PIHC3 metadata entity has a pending draft. This keeps the local node selection aligned with the header-level dirty metadata list before Apply writes changes back.

## Changes

- Matched selected diagram node identifiers against pending diagram changed entities.
- Rendered a compact pending metadata marker in the selection panel with entity id and source path.
- Added English and Chinese label coverage for the marker.
- Added warning-state styling that fits the existing diagram inspector.
- Added a static React regression test for a dirty PIHC3 focus metadata node.

## Verification

- Red test first: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx -t "marks the selected node when its PIHC3 metadata draft is pending"` failed on the missing marker.
- Focused green: same command passed after implementation.
- Diagram view coverage: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx` passed.
- Adjacent metadata/selection coverage: `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/ModuleEditor.test.tsx src/moduleEditor/diagramMetadata.test.ts src/moduleEditor/diagramSelection.test.ts src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts` passed.
- Full desktop unit suite: `rtk npm --prefix apps/desktop run test:unit` passed.
- Desktop build: `rtk npm --prefix apps/desktop run build` passed with the existing Vite large chunk warning.
- Browser smoke: Vite rendered the shell at `http://127.0.0.1:5201/?smoke=selected-draft`, showed no console warnings or errors, and selected the unique project option button named `国家`.
- Whitespace check: `rtk git diff --check -- apps/desktop/src/diagramEditor/ProjectDiagramView.tsx apps/desktop/src/diagramEditor/ProjectDiagramView.test.tsx apps/desktop/src/i18n/locales/en.ts apps/desktop/src/i18n/locales/zh.ts apps/desktop/src/styles/app.css` passed.

## Notes

Plain Vite cannot exercise the real Tauri SDK bridge, so the browser smoke intentionally observed the desktop fallback panel. The React regression test covers the selected-node pending metadata marker itself.
