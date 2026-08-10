# 2026-06-20 12:59 - Inserted Focus Count Fields

## Scope

Kept newly inserted GUI focus-tree entries aligned with PIHC3 migrated metadata that uses per-focus relationship count fields.

## Changes

- Added a regression test for inserting both child and root focuses into a focus list that already uses `prerequisite_count` and `mutually_exclusive_count`.
- Updated the diagram metadata writer to detect relationship count fields in the existing `focuses` list and emit matching fields for newly inserted focus items.
- Preserved compact metadata output for focus lists that do not use relationship count fields.

## Verification

- Red regression: `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts` failed because the inserted child focus lacked `prerequisite_count` and `mutually_exclusive_count`.
- Focused green: `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts` passed with `33` tests.
- Related diagram/editor tests: `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/ModuleEditor.test.tsx` passed with `168` tests.
- Desktop build: `rtk npm --prefix apps/desktop run build` passed, with the existing Vite large-chunk warning.
- Whitespace check: `rtk perl -ne 'if(/[ \t]$/){print "$ARGV:$.: trailing whitespace\n"; $bad=1} END{exit($bad ? 1 : 0)}' apps/desktop/src/moduleEditor/diagramMetadata.ts apps/desktop/src/moduleEditor/diagramMetadata.test.ts` passed.

## Notes

Real PIHC3 focus-tree metadata stores these per-focus counts around prerequisite and mutual-exclusion lists, so GUI-created focuses now keep the migrated summary fields consistent with the surrounding source format.
