# 2026-06-20 13:17 - Diagram Relationship Candidate Guard

## Context

The focus/technology diagram editor already filtered quick relationship candidates, but typed datalist submissions could still pass arbitrary ids to parent, prerequisite, and reference edit callbacks.

## Changes

- Added a shared `diagramCandidateIdFromInput` guard for typed relationship ids.
- Wired parent, prerequisite, and reference form submits through the same candidate whitelist used by quick candidate buttons.
- Added a focused unit test covering accepted, excluded, case-mismatched, and empty candidate inputs.

## Verification

- Red: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
  - Failed before implementation because `diagramCandidateIdFromInput` was not implemented.
- Green: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
  - 86 passed.
- Related: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/layoutModel.test.ts src/moduleEditor/ModuleEditor.test.tsx src/moduleEditor/diagramMetadata.test.ts`
  - 166 passed.
- Build: `rtk npm --prefix apps/desktop run build`
  - Passed with the existing Vite large-chunk warning.
- Browser smoke: `http://127.0.0.1:5174`
  - Title `ParaDev`, nonblank app content, no framework overlay, no console warnings/errors.
  - Filled the module/settings search with `科技`; the visible module list narrowed to the technology module.
- Whitespace: `rtk rg -n "[ \t]+$" apps/desktop/src/diagramEditor/ProjectDiagramView.tsx apps/desktop/src/diagramEditor/ProjectDiagramView.test.tsx`
  - No trailing whitespace.

## Notes

This keeps the GUI relationship edit surface aligned with the canonical diagram candidate rules before metadata writes reach PIHC3 source files.
