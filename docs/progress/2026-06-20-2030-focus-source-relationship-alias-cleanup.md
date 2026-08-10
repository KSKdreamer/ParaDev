# 2026-06-20 20:30 Focus Source Relationship Alias Cleanup

## Summary

- Added PIHC3 focus source relationship regressions for legacy singular `prerequisite` aliases.
- Made canonical source `prerequisites` lists override stale singular source aliases during diagram projection.
- Made source-backed relationship writeback remove legacy alias blocks before inserting canonical relationship lists.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/projectDiagram.test.ts src/moduleEditor/diagramMetadata.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- src/components/Workspace.test.tsx src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts src/moduleEditor/diagramMetadata.test.ts`
- `rtk npm --prefix apps/desktop run build`
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k focus_tree_importer_extracts_source_localization_and_image_metadata_contract`

## Notes

- Vite still reports the pre-existing large chunk warning for the production build.
