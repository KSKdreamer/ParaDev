# 2026-06-20 12:50 - Focus Relationship Counts

## Scope

Kept PIHC3 focus-tree metadata count fields aligned when diagram relationship edits update prerequisites or mutual exclusions.

## Changes

- Added a regression test for PIHC3-style `prerequisite_count` and `mutually_exclusive_count` fields in focus metadata.
- Updated the diagram metadata writer so existing relationship count fields are synchronized with edited relationship lists.
- Preserved PIHC3 field ordering by inserting `prerequisites` after `prerequisite_count` and `mutually_exclusive` after `mutually_exclusive_count` when those count fields exist.

## Verification

- Red regression: `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts` failed with stale `0` counts after adding diagram dependency/reference edges.
- Focused green: `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts` passed with `31` tests.
- Related diagram/editor tests: `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/ModuleEditor.test.tsx` passed with `166` tests.
- Desktop build: `rtk npm --prefix apps/desktop run build` passed, with the existing Vite large-chunk warning.

## Notes

The count fields are present in real PIHC3 focus tree metadata such as `projects/PIHC3/src/modules/focus_tree/C01_MAIN/meta.yaml`, so this keeps GUI diagram edits from leaving stale migration metadata behind.
