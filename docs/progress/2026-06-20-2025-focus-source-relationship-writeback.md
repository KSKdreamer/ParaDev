# 2026-06-20 20:25 Focus Source Relationship Writeback

## Summary

- Added source-backed PIHC3 focus relationship coverage for diagram projection and metadata draft writes.
- Made the diagram adapter prefer `settings.source_focuses` prerequisite and mutual-exclusion fields when those source fields exist.
- Made focus relationship edits write to the matching `source_focuses[].focus_id` item before falling back to compiled `focuses[].id`.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/projectDiagram.test.ts src/moduleEditor/diagramMetadata.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- src/components/Workspace.test.tsx src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts src/moduleEditor/diagramMetadata.test.ts`
- `rtk npm --prefix apps/desktop run build`
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k focus_tree_importer_extracts_source_localization_and_image_metadata_contract`

## Notes

- Vite still reports the pre-existing large chunk warning for the production build.
