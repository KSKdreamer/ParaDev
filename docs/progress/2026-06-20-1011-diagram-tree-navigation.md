# 2026-06-20 10:11 - Diagram Tree Navigation

## Scope

Improved the selected-node context in the desktop diagram editor so PIHC3 focus and technology tree work can navigate parent and child relationships without guessing raw IDs.

## Changes

- Reused the diagram node candidate map for selected-node tree context.
- Replaced the raw parent-only text with a title-aware selectable parent chip.
- Added title-aware selectable child chips while preserving the existing child count.
- Kept selection callbacks and relationship removals keyed by raw node IDs.
- Added English and Chinese labels for parent and child tree navigation actions.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/ModuleEditor.test.tsx src/moduleEditor/diagramMetadata.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- --run`
- `rtk npm --prefix apps/desktop run build`
- `rtk git diff --check`
- Browser smoke on `http://127.0.0.1:5190/?smoke=diagram-tree-navigation`: loaded the desktop shell, opened Technology, confirmed the startup overlay cleared, and saw zero warning/error logs.

## Notes

Plain Vite still shows the expected "SDK browser unavailable" project-browser fallback because the Tauri SDK bridge is not present there. The exact tree navigation DOM is covered by the diagram render test.

No Python files were changed in this slice, so the heaven-style Python scan was not applicable.
