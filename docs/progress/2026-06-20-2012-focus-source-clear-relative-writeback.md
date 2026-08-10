# Focus Source Clear And Relative Writeback

## Summary

Extended the source-backed focus metadata writeback path so auto-layout and relative-position commands update `settings.source_focuses` before falling back to compiled `settings.focuses`.

## Changes

- Added regressions for source-backed focus auto-layout cleanup and relative-position conversion.
- Made focus position clearing and legacy offset clearing prefer `source_focuses[].focus_id` rows.
- Made `relative_position_id` updates source-first and kept new source layout keys after stable identity fields such as `source_path`.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts`
- `rtk npm --prefix apps/desktop run build`
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'focus_tree_importer_extracts_source_localization_and_image_metadata_contract'`
