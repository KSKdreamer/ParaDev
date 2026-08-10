# 2026-06-20 19:23 - Focus Source Layout Metadata

## Summary

- Preserved PIHC2 scalar focus layout fields in migrated `settings.source_focuses` records: `tree`, `parent`, `x`, `y`, `dx`, `dy`, `cx`, `cy`, `w`, `pw`, `dw`, `dc`, and `priority`.
- Kept the metadata flat so ParaDev SDK/CLI callers can generate batch focus updates without learning a second layout schema.
- Updated the desktop diagram adapter to prefer `source_focuses` layout metadata when migrated PIHC2 records carry legacy positioning fields, so compiled final `x/y` does not shadow `parent` + `dx/dy`.
- Added adapter coverage for source-only legacy offsets, priorities, subtree deltas, center offsets, and source focus image hydration.
- Extended the PIHC3 focus migration contract with real C08_PARTII root, relative-offset, and priority examples.

## Validation

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/projectDiagram.test.ts`
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -k focus_tree_importer_extracts_source_localization_and_image_metadata_contract`
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -k focus_tree_importer`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_focuses.py tests/test_pihc3_migration_contracts.py`
- `rtk npm --prefix apps/desktop run build`

The Vite build still reports the existing large-chunk warning.
