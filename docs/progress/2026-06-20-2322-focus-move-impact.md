# 2026-06-20 23:22 - Focus Move Impact

## Context

The focus tree editor now has explicit Branch, Node, Node only, and Reflow movement modes. The controls still did not show how many focus nodes the active mode would affect, which made branch and reflow movement harder to reason about on larger HOI4-style trees.

## Changes

- Added a compact active move impact chip beside the selected-node move mode controls.
- Reused `diagramDragPreviewNodeIds` for the count so the chip matches the exact affected-node set used by drag previews.
- Added English and Chinese strings for singular and plural impact text.
- Added regression coverage for the formatter and rendered impact chip.

## Verification

- Red test first: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx` failed because `diagramMoveImpactText` and `.project-diagram-move-impact` did not exist.
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/ModuleEditor.test.tsx src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts src/styles/diagram.test.ts src/App.test.ts src/components/AppShell.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts src/components/AppShell.test.tsx src/components/ProjectPanel.test.tsx src/components/Workspace.test.tsx src/moduleEditor/ModuleEditor.test.tsx src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/diagramImages.test.ts src/diagramEditor/diagramHistory.test.ts src/moduleEditor/diagramMetadata.test.ts src/styles/diagram.test.ts`
- `rtk npm --prefix apps/desktop run build`
- Browser QA at `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html` through the in-app browser:
  - Smoke page rendered 10 focus nodes, 10 routed edges, and 9 focus node images.
  - Initial Branch mode showed `Affects 3 nodes` for the selected smoke branch.
  - Clicking Reflow kept the same affected count and switched the pressed mode to Reflow.
  - Recent console logs contained only Vite and React development messages, with no warning or error entries.

## Notes

This improves mode discovery without changing layout semantics. The affected count intentionally follows the same helper as drag previews, so future movement-policy changes update the chip and preview together.
