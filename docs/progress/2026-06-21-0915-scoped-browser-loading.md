# 2026-06-21 09:15 - Scoped Browser Loading State

## Context

The desktop GUI now loads heavy project browser families on demand so focus-tree images can hydrate from PIHC3 source assets without blocking startup. That made diagram tabs briefly look like the SDK browser was unavailable while a scoped family request was still in flight.

## Changes

- Added per-scope loading tracking in `apps/desktop/src/App.tsx`, keyed by the same project root and SDK browser scope used for lazy family payloads.
- Passed active and secondary pane loading state through `AppShell` and `Workspace`, including split-view support.
- Added a localized `ModuleEditor` loading panel for module and diagram surfaces so focus/technology diagram tabs show an intentional status before scoped data arrives.
- Added tests for the scoped loading selector, workspace pane pass-through, and module editor loading fallback.

## Verification

```bash
rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/ModuleEditor.test.tsx src/components/Workspace.test.tsx src/App.test.ts
rtk npm --prefix apps/desktop run test:unit -- src/services/paradev.test.ts src/App.test.ts src/components/Workspace.test.tsx src/moduleEditor/ModuleEditor.test.tsx src/diagramEditor/sourceBackedSmokeModel.test.ts src/diagramEditor/projectDiagram.test.ts src/moduleEditor/diagramMetadata.test.ts src/diagramEditor/diagramImages.test.ts src/diagramEditor/ProjectDiagramView.test.tsx
rtk npm --prefix apps/desktop run build
rtk npm --prefix apps/desktop run test:unit -- src/components/AppShell.test.tsx src/services/paradev.test.ts src/App.test.ts src/components/Workspace.test.tsx src/moduleEditor/ModuleEditor.test.tsx src/diagramEditor/sourceBackedSmokeModel.test.ts src/diagramEditor/projectDiagram.test.ts src/moduleEditor/diagramMetadata.test.ts src/diagramEditor/diagramImages.test.ts src/diagramEditor/ProjectDiagramView.test.tsx
```

All commands passed. The build still reports the existing Vite chunk-size warning.

Manual browser smoke check: opened `http://127.0.0.1:5180/e2e/diagram-tab-smoke.html`, selected `National Focuses diagram`, and confirmed 9 SVG image nodes rendered with 34x34 icon images in the diagram panel.
