# 2026-06-20 21:38 - Module and Diagram Tab Routing

## Summary

- Kept normal module selection routed to the normal module workspace tab instead of auto-opening the focus or technology diagram.
- Added a separate project-panel diagram section for diagram-capable module families, currently focus trees and technologies.
- Wired the separate diagram rows to open diagram workspace tabs and highlight the active diagram row.
- Verified the diagram pipeline still renders focus nodes as SVG image-backed nodes and preserves PIHC-style layout fields such as `x`, `y`, `dx`, `dy`, `cx`, `cy`, `w`, `dw`, `dc`, and `priority`.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts src/components/ProjectPanel.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts src/components/AppShell.test.tsx src/components/ProjectPanel.test.tsx src/components/Workspace.test.tsx src/moduleEditor/ModuleEditor.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts src/components/AppShell.test.tsx src/components/ProjectPanel.test.tsx src/components/Workspace.test.tsx src/moduleEditor/ModuleEditor.test.tsx src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/diagramJson.test.ts src/moduleEditor/diagramMetadata.test.ts src/styles/diagram.test.ts`
- `rtk npm --prefix apps/desktop run build`
- Browser QA at `http://127.0.0.1:5180/`, viewport 1440 x 900:
  - Normal `国策` row opened `data-tab-kind="module"`.
  - Separate `国策图谱` row opened `data-tab-kind="diagram"`.
  - Diagram workspace shell measured 1200 x 806 CSS px.
  - Screenshot saved outside the worktree at `/tmp/paradev-project-panel-diagram-routes.png`.
