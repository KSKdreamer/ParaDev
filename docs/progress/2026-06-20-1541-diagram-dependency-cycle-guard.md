# Diagram Dependency Cycle Guard Progress

Date: 2026-06-20 15:41

Linear: TAL-000

## Done

- Added a diagram model guard that rejects dependency edges when the target already reaches the source through dependency links.
- Covered direct and transitive prerequisite cycles while keeping forward redundant unlock edges valid.
- Kept the rule at the canonical diagram command layer so focus and technology tree edits share it.
- Filtered transitive unlock descendants out of the selected-node prerequisite candidate list so the GUI does not offer no-op cyclic edits.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/layoutModel.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/layoutModel.test.ts src/diagramEditor/projectDiagram.test.ts src/moduleEditor/diagramMetadata.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/layoutModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/projectDiagram.test.ts src/moduleEditor/diagramMetadata.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`

## Risks Or Blockers

- Desktop build still reports the existing Vite large-chunk warning.
- The diagram editor files are currently untracked in this worktree, so normal `git diff` does not show their changes until staged.

## Next

- Continue tightening focus and technology tree editor commands against PIHC3 metadata edge cases.
