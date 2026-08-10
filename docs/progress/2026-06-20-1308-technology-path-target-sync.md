# 2026-06-20 13:08 - Technology Path Target Sync

## Scope

Kept PIHC3 technology source-side path summaries aligned when GUI diagram dependency edges change.

## Changes

- Added a regression test for adding a technology dependency edge where the source module already uses `path_count` and `path_target_ids`.
- Added source-side dependency target detection so changed metadata entity ids include the source technology as well as the target technology.
- Added technology metadata writing for `path_count` and `path_target_ids`, using `path_count` as the preferred insertion anchor.

## Verification

- Red regression: `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts` failed because only the target technology was marked changed.
- Focused green: `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts` passed with `35` tests.
- Related diagram/editor tests: `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/ModuleEditor.test.tsx` passed with `170` tests.
- Desktop build: `rtk npm --prefix apps/desktop run build` passed, with the existing Vite large-chunk warning.
- Whitespace check: `rtk perl -ne 'if(/[ \t]$/){print "$ARGV:$.: trailing whitespace\n"; $bad=1} END{exit($bad ? 1 : 0)}' apps/desktop/src/moduleEditor/diagramMetadata.ts apps/desktop/src/moduleEditor/diagramMetadata.test.ts` passed.

## Notes

Real PIHC3 technology metadata stores target-side `dependency_ids` and source-side `path_count` / `path_target_ids`. The GUI metadata draft path now keeps both sides discoverable when dependency edges are added or removed in the technology diagram.
