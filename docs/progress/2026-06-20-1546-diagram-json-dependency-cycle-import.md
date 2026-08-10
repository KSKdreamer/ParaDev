# Diagram JSON Dependency Cycle Import Progress

Date: 2026-06-20 15:46

Linear: TAL-000

## Done

- Added canonical dependency-cycle detection for diagram documents.
- Reused the dependency-cycle rule during JSON import so pasted/exported focus or technology diagrams cannot bypass editor command guards.
- Covered imported transitive prerequisite cycles with a focused JSON import test.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJson.test.ts src/diagramEditor/layoutModel.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/diagramMetadata.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`

## Risks Or Blockers

- Desktop build still reports the existing Vite large-chunk warning.
- The diagram editor files are currently untracked in this worktree, so normal `git diff` does not show their changes until staged.

## Next

- Continue hardening diagram import and editor commands around PIHC3 focus and technology metadata invariants.
