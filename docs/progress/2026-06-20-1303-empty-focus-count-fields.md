# 2026-06-20 13:03 - Empty Focus Count Fields

## Scope

Kept the first GUI-created focus in an empty PIHC3 focus tree aligned with migrated focus metadata.

## Changes

- Added a regression test using the real PIHC3 empty-tree shape: `focus_count: 0` plus `focuses: []`.
- Updated focus insertion metadata formatting so an existing `focus_count` before `focuses` implies PIHC3 count-field style even when there are no focus rows yet.
- Preserved compact output for generic empty focus lists that do not declare `focus_count`.

## Verification

- Red regression: `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts` failed because the first inserted focus had no `prerequisite_count` or `mutually_exclusive_count`.
- Focused green: `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts` passed with `34` tests.
- Related diagram/editor tests: `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/ModuleEditor.test.tsx` passed with `169` tests.
- Desktop build: `rtk npm --prefix apps/desktop run build` passed, with the existing Vite large-chunk warning.
- Whitespace check: `rtk perl -ne 'if(/[ \t]$/){print "$ARGV:$.: trailing whitespace\n"; $bad=1} END{exit($bad ? 1 : 0)}' apps/desktop/src/moduleEditor/diagramMetadata.ts apps/desktop/src/moduleEditor/diagramMetadata.test.ts` passed.

## Notes

PIHC3 empty focus-tree modules such as `C02_ALT`, `C02_ALT_OCTAVIA`, and `NULL` already store `focus_count: 0` next to `focuses: []`. The first GUI add operation now preserves the same migrated count-field contract used by non-empty PIHC3 focus rows.
