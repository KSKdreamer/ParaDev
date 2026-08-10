# 2026-06-20 10:28 - Focus Entity Diagram Selection

## Scope

Improved the desktop focus-tree editor selection bridge for PIHC3. Opening or selecting a focus-tree module now resolves to a concrete embedded focus node in the diagram instead of passing the module object id as a diagram node id.

## Changes

- Added `diagramNodeIdForEntity(...)` as the reverse of diagram-node-to-module selection.
- Preserved the currently selected embedded focus node when it still belongs to the selected module entity.
- Fell back to direct technology node ids first, then the first matching embedded focus node.
- Updated `ModuleEditor` to pass the resolved diagram node id into `ProjectDiagramView`.
- Added helper and static render tests for focus-tree module selection.

## Verification

- Red test first: `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramSelection.test.ts src/moduleEditor/ModuleEditor.test.tsx` failed on the missing helper and missing selected-node summary.
- `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramSelection.test.ts src/moduleEditor/ModuleEditor.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/model.test.ts src/moduleEditor/ModuleEditor.test.tsx src/moduleEditor/diagramSelection.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/projectDiagram.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- --run`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke on `http://127.0.0.1:5194/?smoke=focus-entity-diagram-selection`: loaded the desktop shell, opened Technology, confirmed the startup overlay cleared, confirmed the expected plain-Vite SDK fallback, captured a screenshot, and saw zero warning/error logs.
- `rtk git diff --check`

## Notes

Plain Vite still cannot load SDK-backed PIHC3 browser data, so the exact focus-tree selected-node behavior is covered by the static React integration test rather than the browser smoke.

The Vite production build still emits the existing large-chunk warning for the editor bundles.

No Python files were changed in this slice, so the heaven-style Python scan was not applicable.
