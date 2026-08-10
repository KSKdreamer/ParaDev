# 2026-06-20 23:16 - Focus Edge Preview Classes

## Context

The focus tree editor already highlighted all affected nodes during branch and reflow drag previews. The connected focus-tree lines still looked like normal selected/distant edges, so the pending branch operation did not read as one connected HOI4-style tree.

## Changes

- Added a testable `diagramEdgeClassName` helper that marks an edge as `preview` when both endpoints are in the active drag preview node set.
- Passed the current drag preview node id set into SVG edge rendering.
- Added preview edge CSS so affected routed lines keep full visibility even when they are not directly connected to the selected root node.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/ModuleEditor.test.tsx src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts src/styles/diagram.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts src/components/AppShell.test.tsx src/components/ProjectPanel.test.tsx src/components/Workspace.test.tsx src/moduleEditor/ModuleEditor.test.tsx src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/diagramImages.test.ts src/diagramEditor/diagramHistory.test.ts src/moduleEditor/diagramMetadata.test.ts src/styles/diagram.test.ts`
- `rtk npm --prefix apps/desktop run build`
- Browser QA at `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html` through the in-app browser:
  - Smoke page rendered 10 focus nodes, 10 routed edges, 9 focus node images, and 9 tree edges.
  - Edge preview CSS was present in the rendered stylesheet.
  - `Reflow` move mode was visible, enabled, and became the pressed mode when clicked.
  - Recent console logs contained only Vite and React development messages, with no warning or error entries.

## Notes

The browser check verifies rendered surface health and mode selection. The exact transient edge preview state is covered by unit tests because stable mid-drag sampling through the browser bridge remains unreliable.
