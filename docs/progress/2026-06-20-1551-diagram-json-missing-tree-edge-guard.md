# Diagram JSON Missing Tree Edge Guard Progress

Date: 2026-06-20 15:51

Linear: TAL-000

## Done

- Added canonical detection for parented diagram nodes whose matching tree edge is missing.
- Reused the rule during JSON import so pasted focus or technology diagrams cannot hide tree links that will still affect layout and metadata saves.
- Covered imported parent ids without matching tree edges with a focused JSON import test.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJson.test.ts src/diagramEditor/layoutModel.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/diagramMetadata.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`

## Risks Or Blockers

- Desktop build still reports the existing Vite large-chunk warning.
- The diagram editor files are currently untracked in this worktree, so normal `git diff` does not show their changes until staged.

## Next

- Continue hardening focus and technology diagram import/edit flows against PIHC3 metadata drift.
