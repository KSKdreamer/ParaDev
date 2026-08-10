# 2026-06-20 22:53 - Focus Drag Mode Selector

## Context

The focus tree editor now has compact movement modes, but pointer dragging still used only modifier keys. That made the visible `Branch` / `Node` / `Reflow` selector incomplete: the pad followed it, while plain drag still behaved like node movement unless the user remembered Shift/Cmd/Ctrl.

## Changes

- Lifted selected move mode into `ProjectDiagramView` state so toolbar buttons, drag preview, drag commit, and focused-node arrow movement share the same mode.
- Made plain pointer drag use the active mode by default:
  - `Branch` drags the selected branch.
  - `Node` drags only the selected node movement mode.
  - `Reflow` drags the node and auto-layouts descendants.
- Kept Shift, Alt, and Cmd/Ctrl as explicit overrides for branch, node-only, and reflow movement.
- Updated selected-node drag hints so the first hint describes the current plain-drag behavior.
- Added English and Chinese labels for active drag mode hints.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/ModuleEditor.test.tsx src/diagramEditor/ProjectDiagramView.test.tsx src/styles/diagram.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts src/components/AppShell.test.tsx src/components/ProjectPanel.test.tsx src/components/Workspace.test.tsx src/moduleEditor/ModuleEditor.test.tsx src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/diagramImages.test.ts src/diagramEditor/diagramHistory.test.ts src/moduleEditor/diagramMetadata.test.ts src/styles/diagram.test.ts`
- `rtk npm --prefix apps/desktop run build`
- Browser QA at `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html?drag-mode=1` with a 1440x900 viewport:
  - Initial `Branch` mode showed branch pad labels and `Drag branch` hint.
  - Clicking `Node` switched the pad labels to selected-node movement and showed `Drag node`.
  - Clicking `Reflow` switched the pad labels to descendant relayout movement and showed `Drag node and auto-layout descendants`.
  - Old repeated movement control classes remained absent.
  - Console check returned 0 warnings and 0 errors.
