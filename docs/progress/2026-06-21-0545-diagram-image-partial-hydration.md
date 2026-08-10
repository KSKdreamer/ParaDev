# Diagram Image Partial Hydration Progress

Date: 2026-06-21 05:45 +0800

Linear: TAL-000

## Done

- Made diagram image hydration fail per node instead of clearing every hydrated image when one local focus or technology icon cannot be loaded.
- Added a focused regression that keeps a valid PIHC3 migrated focus preview visible when a neighboring local preview path fails.

## Verification

- Red check: `rtk bash -lc 'cd apps/desktop && npm run test:unit -- src/diagramEditor/diagramImages.test.ts'` failed because the missing preview rejection escaped `loadDiagramImageUrls(...)`.
- Green focused check: `rtk bash -lc 'cd apps/desktop && npm run test:unit -- src/diagramEditor/diagramImages.test.ts'`.
- Diagram coverage: `rtk bash -lc 'cd apps/desktop && npm run test:unit -- src/diagramEditor/diagramImages.test.ts src/diagramEditor/projectDiagram.test.ts src/diagramEditor/ProjectDiagramView.test.tsx'`.
- Desktop build/type check: `rtk bash -lc 'cd apps/desktop && npm run build'`.
- Whitespace check: `rtk git diff --check -- apps/desktop/src/diagramEditor/diagramImages.ts apps/desktop/src/diagramEditor/diagramImages.test.ts docs/progress/README.md docs/progress/2026-06-21-0545-diagram-image-partial-hydration.md`.

## Risks Or Blockers

- The broader worktree still includes earlier active-goal GUI, PIHC3, and SDK/CLI changes. This checkpoint only changes diagram image hydration behavior.

## Next

- Continue improving normal-window focus and technology diagram usability with PIHC3-backed smoke coverage.
