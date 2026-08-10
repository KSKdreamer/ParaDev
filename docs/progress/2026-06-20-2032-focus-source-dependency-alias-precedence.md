# 2026-06-20 20:32 Focus Source Dependency Alias Precedence

## Summary

- Added a PIHC3 focus source projection regression for canonical `prerequisites` versus stale dependency alias lists such as `dependency_ids`.
- Made diagram dependency projection treat source `prerequisites` as the authoritative dependency field when present.
- Kept legacy dependency aliases available only when the canonical source list is absent.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/projectDiagram.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- src/components/Workspace.test.tsx src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts src/moduleEditor/diagramMetadata.test.ts`
- `rtk npm --prefix apps/desktop run build`
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k focus_tree_importer_extracts_source_localization_and_image_metadata_contract`

## Notes

- Vite still reports the pre-existing large chunk warning for the production build.
