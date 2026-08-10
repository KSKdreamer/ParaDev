# 2026-06-20 22:44 - Focus Move Mode Controls

## Context

The HOI4 focus tree toolbar still exposed selected-node movement as repeated arrow clusters. At normal desktop widths the controls could be pushed off-screen, which made branch movement hard to discover after the focus tree moved closer to a grid-like HOI4 editor.

## Changes

- Replaced repeated selected-node movement arrow groups with one move-mode strip and one direction pad.
- Defaulted the selected mode to branch movement when subtree movement is available.
- Kept node-only and descendant-reflow movement as explicit modes instead of separate arrow clusters.
- Let the diagram toolbar wrap and gave selected-node tools a full-width wrapped row so controls stay visible in normal windows.
- Added English and Chinese labels for the move-mode selector.
- Updated React integration and CSS regression tests for the compact move controls and wrapping toolbar.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/ModuleEditor.test.tsx src/diagramEditor/ProjectDiagramView.test.tsx src/styles/diagram.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts src/components/AppShell.test.tsx src/components/ProjectPanel.test.tsx src/components/Workspace.test.tsx src/moduleEditor/ModuleEditor.test.tsx src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/diagramImages.test.ts src/diagramEditor/diagramHistory.test.ts src/moduleEditor/diagramMetadata.test.ts src/styles/diagram.test.ts`
- `rtk npm --prefix apps/desktop run build`
- Browser QA at `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html?move-mode=2` with a 1440x900 viewport:
  - Move mode controls rendered at x=27..306 inside the viewport.
  - Main action row used `flex-wrap: wrap` and visible overflow.
  - Old repeated movement control classes were absent.
  - Console check returned 0 warnings and 0 errors.
