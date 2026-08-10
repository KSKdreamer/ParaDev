# 2026-06-20 12:54 - Focus Count Sync

## Scope

Kept PIHC3 focus-tree `focus_count` metadata aligned when GUI diagram edits add or remove focuses.

## Changes

- Added a regression test for `focus_count` updates on root focus insertion and focus branch removal.
- Updated the diagram metadata writer to count draft embedded focus nodes per focus-tree entity and sync an existing `focus_count` field after applying focus list edits.
- Kept the writer conservative: it updates `focus_count` when the field already exists and does not add the field to metadata that does not use it.

## Verification

- Red regression: `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts` failed with `focus_count: 2` after adding a third focus.
- Focused green: `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts` passed with `32` tests.
- Related diagram/editor tests: `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/ModuleEditor.test.tsx` passed with `167` tests.
- Desktop build: `rtk npm --prefix apps/desktop run build` passed, with the existing Vite large-chunk warning.

## Notes

Real PIHC3 focus-tree metadata stores `focus_count` next to the `focuses` list, so this prevents GUI add/remove operations from leaving stale migration summary fields behind.
