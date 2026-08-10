# 2026-06-20 10:35 - Focus Selected Node Detail

## Scope

Improved the desktop focus-tree editor selection bridge for PIHC3. When a module detail panel is open and the diagram selection is an embedded focus node, the detail header now exposes that active diagram node id so users can keep context while editing the broader focus-tree module.

## Changes

- Added an active diagram node marker to `ModuleEntityDetails`.
- Derived the marker in `ModuleEditor` only when the selected diagram node is an embedded child rather than the selected entity/module id.
- Added English and Chinese translations for the marker text.
- Added focused styling so the marker fits in the compact module detail header.
- Extended the focus-tree static render test to assert the selected embedded node appears in the detail header.

## Verification

- Red test first: `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/ModuleEditor.test.tsx` failed on the missing `entity-selected-node` marker.
- `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/ModuleEditor.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/model.test.ts src/moduleEditor/ModuleEditor.test.tsx src/moduleEditor/diagramSelection.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/projectDiagram.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/ModuleEditor.test.tsx src/moduleEditor/ModuleEntityDetails.test.tsx src/moduleEditor/diagramSelection.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- --run`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke on `http://127.0.0.1:5196/?smoke=focus-selected-node-header`: loaded the desktop shell, opened Technology, confirmed the startup overlay cleared, confirmed the expected plain-Vite SDK fallback, captured a screenshot, and saw zero warning/error logs.
- `rtk git diff --check`

## Notes

Plain Vite still cannot load SDK-backed PIHC3 browser data, so the exact selected-node header behavior is covered by the static React integration test rather than the browser smoke.

The Vite production build still emits the existing large-chunk warning for the editor bundles.

No Python files were changed in this slice, so the heaven-style Python scan was not applicable.
