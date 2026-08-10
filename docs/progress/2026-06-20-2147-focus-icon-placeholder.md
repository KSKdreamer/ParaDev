# 2026-06-20 21:47 - Focus Icon Placeholder

## Summary

- Added a visible SVG placeholder inside focus nodes when a local focus icon path exists but thumbnail hydration has not produced a browser-safe image URL.
- Kept successfully hydrated focus icons unchanged; the fallback only appears for missing or still-loading local images.
- Extended the diagram apply-review smoke fixture to cover both paths: a hydrated focus icon and a deliberately missing local focus icon.
- Reused the smoke page React root across Vite reloads so repeated browser QA does not trigger `createRoot()` warnings.

## Verification

- Red test first:
  - `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx src/styles/diagram.test.ts`
  - Failed on missing placeholder markup and missing placeholder CSS blocks.
- Green focused test:
  - `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx src/styles/diagram.test.ts`
  - 2 files, 107 tests passed.
- Broader desktop diagram unit slice:
  - `rtk npm --prefix apps/desktop run test:unit -- src/App.test.ts src/components/AppShell.test.tsx src/components/ProjectPanel.test.tsx src/components/Workspace.test.tsx src/moduleEditor/ModuleEditor.test.tsx src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/diagramImages.test.ts src/diagramEditor/diagramHistory.test.ts src/moduleEditor/diagramMetadata.test.ts src/styles/diagram.test.ts`
  - 14 files, 293 tests passed.
- Build:
  - `rtk npm --prefix apps/desktop run build`
  - Passed with the existing large-chunk Vite warning.
- Browser QA at `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html`:
  - Page title: `ParaDev Diagram Apply Review Smoke`.
  - Nonblank DOM included `Diagram apply review smoke`, `Part IV`, and `Canterlot`.
  - No framework overlay detected.
  - Timestamp-filtered console errors/warnings: none.
  - Hydrated focus image count: 1 on `C08_PARTIV`.
  - Missing-icon placeholder count: 1 on `C09_CANTERLOT`.
  - Apply review flow changed `applyCount` from `0` to `1` and dirty state from `1` to `0`.
  - Screenshot saved outside the worktree at `/tmp/paradev-diagram-focus-icon-placeholder.png`.
