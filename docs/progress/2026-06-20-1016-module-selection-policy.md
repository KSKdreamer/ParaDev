# 2026-06-20 10:16 - Module Selection Policy

## Scope

Improved the desktop module editor selection policy for PIHC3 diagram workflows. Diagram node selection can map to a module entity that is hidden by the current entity-list filter, and the editor should keep that module selected instead of snapping back to the first visible row.

## Changes

- Added `resolveModuleEntitySelection(...)` as the shared module-selection policy.
- Preserved current selections that still exist in the full module entity set, even when filtered out of the visible list.
- Fell back to the first visible entity, then the first full entity, only when the current selection is missing.
- Updated `ModuleEditor` to use the shared policy in its selection reconciliation effect.

## Verification

- Red test first: `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/model.test.ts` failed on the missing helper.
- `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/model.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/ModuleEditor.test.tsx src/moduleEditor/diagramSelection.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/model.test.ts src/moduleEditor/ModuleEditor.test.tsx src/moduleEditor/diagramSelection.test.ts src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- --run`
- `rtk npm --prefix apps/desktop run build`
- `rtk git diff --check`
- Browser smoke on `http://127.0.0.1:5190/?smoke=module-selection-policy`: loaded the desktop shell, opened Technology, confirmed the startup overlay cleared, confirmed the expected plain-Vite SDK fallback, and saw zero warning/error logs.

## Notes

The Vite production build still emits the existing large-chunk warning for the editor bundles.

No Python files were changed in this slice, so the heaven-style Python scan was not applicable.
