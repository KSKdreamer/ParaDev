# Focus Diagram Scope Selector Progress

Date: 2026-06-21 11:30

Linear: TAL-000

## Done

- Added a compact focus-tree selector to dedicated focus diagram tabs so users can switch scoped PIHC focus trees inside the diagram editor.
- Kept technology diagram tabs selector-free and family-level.
- Extended the diagram-tab smoke fixture with a second focus tree and dataset counters for scope options, current scope, C09 node presence, and migrated focus image hydration.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/ModuleEditor.test.tsx -t "shows a focus tree scope selector"`
- `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/ModuleEditor.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/ModuleEditor.test.tsx src/diagramEditor/projectDiagram.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/diagramImages.test.ts src/diagramEditor/sourceBackedSmokeModel.test.ts`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke at `http://127.0.0.1:5180/e2e/diagram-tab-smoke.html`: selector options `C08 Part IV,C09 Main`, C08 image hydration `Images 9/9` with 0 placeholders, switching to `focus_tree:C09_MAIN` removes C08 nodes and shows the C09 node, and normal-window selector/panel boxes do not overlap.

## Risks Or Blockers

- Switching is disabled while diagram edits are dirty; the next usability pass should make this state clearer near the selector.

## Next

- Add a focused apply/discard affordance near the scope selector when dirty edits block focus-tree switching.
