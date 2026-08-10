# 2026-06-20 20:35 Focus Source Relative Position Readback

## Summary

- Added a PIHC3 source focus projection regression for `source_focuses[].relative_position_id`.
- Made source focus layout extraction include relative parent fields, so GUI-written source relative positions reopen as relative focus nodes.
- Verified source `relative_position_id` plus `x/y` offsets override stale compiled absolute focus coordinates.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/projectDiagram.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- src/components/Workspace.test.tsx src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts src/moduleEditor/diagramMetadata.test.ts`
- `rtk npm --prefix apps/desktop run build`
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k focus_tree_importer_extracts_source_localization_and_image_metadata_contract`

## Notes

- Vite still reports the pre-existing large chunk warning for the production build.
