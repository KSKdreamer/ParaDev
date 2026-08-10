# 2026-06-20 13:11 - Technology Empty List Preservation

## Scope

Kept PIHC3 technology relationship metadata fields present when GUI diagram edits remove the last dependency edge.

## Changes

- Updated the technology dependency removal regression so `dependency_ids` returns to `[]` instead of disappearing.
- Added a source-side regression for `path_count: 0` plus `path_target_ids: []` after removing the last outgoing technology path edge.
- Added an explicit `keepEmpty` option to scalar-list upserts and enabled it only for technology `dependency_ids` and `path_target_ids`.

## Verification

- Red regression: `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts` failed because the writer dropped `dependency_ids` and `path_target_ids` when lists became empty.
- Focused green: `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts` passed with `36` tests.
- Related diagram/editor tests: `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/ModuleEditor.test.tsx` passed with `171` tests.
- Desktop build: `rtk npm --prefix apps/desktop run build` passed, with the existing Vite large-chunk warning.
- Whitespace check: `rtk perl -ne 'if(/[ \t]$/){print "$ARGV:$.: trailing whitespace\n"; $bad=1} END{exit($bad ? 1 : 0)}' apps/desktop/src/moduleEditor/diagramMetadata.ts apps/desktop/src/moduleEditor/diagramMetadata.test.ts` passed.

## Notes

PIHC3 technology metadata commonly keeps `dependency_ids: []`, `path_count: 0`, and `path_target_ids: []` for root or terminal technologies. The GUI draft writer now preserves that migration contract without changing focus-tree zero-count list behavior.
