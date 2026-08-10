# Focus Source Writeback

## Summary

Aligned diagram metadata writeback with PIHC2-derived `source_focuses` layout metadata so GUI focus moves persist to the migrated source-layout rows before falling back to compiled `focuses` rows.

## Changes

- Added regressions for moved focus nodes whose PIHC layout comes from `settings.source_focuses`.
- Made `updateFocusPosition` and `updateFocusLegacyOffset` prefer `source_focuses[].focus_id` ranges when those rows exist.
- Kept compiled `settings.focuses` coordinates unchanged in those source-backed cases, preserving the imported parity summary while the editor-owned layout metadata changes.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts src/diagramEditor/projectDiagram.test.ts`
- `rtk npm --prefix apps/desktop run build`
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'focus_tree_importer_extracts_source_localization_and_image_metadata_contract'`
