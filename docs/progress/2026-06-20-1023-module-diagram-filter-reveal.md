# 2026-06-20 10:23 - Diagram Selection Filter Reveal

## Scope

Improved the desktop module editor workflow for PIHC3 focus/technology diagram browsing. When a diagram node maps to a module entity hidden by the current entity-list filter, the editor now clears the filter so the selected module row becomes visible.

## Changes

- Added `resolveModuleEntityQueryAfterExternalSelection(...)` as the shared policy for external diagram selections.
- Preserved the current entity-list filter when the externally selected entity is already visible.
- Cleared the filter only when the externally selected entity is hidden by it.
- Routed diagram node selection and diagram edit fallback selections through the shared policy.

## Verification

- Red test first: `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/model.test.ts` failed on the missing helper.
- `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/model.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/model.test.ts src/moduleEditor/ModuleEditor.test.tsx src/moduleEditor/diagramSelection.test.ts src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- --run`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke on `http://127.0.0.1:5192/?smoke=module-diagram-selection-query`: loaded the desktop shell, opened Technology, confirmed the startup overlay cleared, confirmed the expected plain-Vite SDK fallback, and saw zero warning/error logs.
- `rtk git diff --check`

## Notes

The Vite production build still emits the existing large-chunk warning for the editor bundles.

No Python files were changed in this slice, so the heaven-style Python scan was not applicable.
