# 2026-06-20 11:09 - Diagram Branch Size Context

## Scope

Improved the desktop focus-tree diagram selected-node panel for PIHC3 editing. When a selected node has descendants, the panel now shows the affected branch size so users can see how many nodes a subtree-level action may touch before using branch layout or branch removal controls.

## Changes

- Added a selected-branch summary row with total branch node count and descendant count.
- Reused existing selected-subtree calculations from branch edit enablement.
- Added English and Chinese translation keys for the branch-size label.
- Added the row to the full-width selected-panel CSS group.
- Added a static React render test for a selected node with one descendant.

## Verification

- Red test first: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx -t "renders selected branch size context"` failed on the missing `project-diagram-selection-subtree` row.
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx -t "renders selected branch size context"`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts src/moduleEditor/ModuleEditor.test.tsx src/moduleEditor/diagramSelection.test.ts src/moduleEditor/diagramMetadata.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- --run`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke on `http://127.0.0.1:5201/?smoke=branch-size`: loaded the desktop shell, saw zero warning/error logs, captured screenshots before and after selecting the 国策 module row, and confirmed the expected plain-Vite SDK browser fallback.
- `rtk git diff --check -- apps/desktop/src/diagramEditor/ProjectDiagramView.tsx apps/desktop/src/diagramEditor/ProjectDiagramView.test.tsx apps/desktop/src/i18n/locales/en.ts apps/desktop/src/i18n/locales/zh.ts apps/desktop/src/styles/app.css`

## Notes

Plain Vite still cannot load SDK-backed PIHC3 browser data, so the exact branch-size selected-panel behavior is covered by the static React integration test rather than browser data smoke. The rendered browser smoke still verifies that the desktop shell loads, has no framework overlay, has no console warnings/errors, and module-row interaction works.

The Vite production build still emits the existing large-chunk warning for editor bundles.
