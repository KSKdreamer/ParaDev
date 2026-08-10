# Diagram Selected Focus Scope Progress

Date: 2026-06-21 11:21

Linear: TAL-000

## Done

- Scoped dedicated focus diagram tabs to the selected focus tree module so a PIHC3 focus canvas does not merge unrelated trees into the same view.
- Kept technology diagrams family-level, preserving their existing graph behavior.
- Rechecked the migrated focus-image canvas coverage after the scoping change.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/ModuleEditor.test.tsx -t "scopes a focus diagram tab"`
- `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/ModuleEditor.test.tsx src/diagramEditor/projectDiagram.test.ts src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/projectDiagram.test.ts src/diagramEditor/diagramImages.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/sourceBackedSmokeModel.test.ts`
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k "focus_asset_component or focus_tree"`

## Risks Or Blockers

- The diagram tab still needs a visible focus-tree selector for switching scoped trees without returning through the module list.

## Next

- Add a compact diagram-scope selector or open-target handoff from the normal module tab.
