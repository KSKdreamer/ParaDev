# 2026-06-21 00:45 Focus Source Layout Preservation

## Context

Continued the focus-tree editor and PIHC3 migration loop after adding rendered focus preview icons. The next gap was preserving PIHC2 layout vocabulary when ParaDev writes focus-tree metadata back from the diagram editor.

## Changes

- Switched focus diagram nodes to compact 2x2 grid tiles for PIHC focus-tree browsing.
- Updated compact focus icon rendering so image-backed focus tiles show the actual icon without the title plaque crowding the tile.
- Synced the diagram apply-review smoke fixture with the same compact 2x2 focus tile dimensions.
- Added regression coverage for legacy PIHC source-focus offsets that use `cx`/`cy`.
- Updated the diagram metadata serializer to keep writing `cx`/`cy` when a focus entry already uses that field pair, instead of normalizing the entry to `dx`/`dy`.
- Regenerated only `C08_PARTIV` through `projects/PIHC3/scripts/migrate_pihc2_focuses.py --only C08_PARTIV` so its `source_focuses` include real editable layout fields such as `x`, `y`, `dx`, and `priority`.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts -t "keeps migrated PIHC source focus cx and cy"` passed.
- `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts src/diagramEditor/projectDiagram.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/layoutModel.test.ts` passed.
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -k focus_tree_importer -q` passed with 2 tests.
- `rtk npm --prefix apps/desktop run test:unit` passed with 418 tests.
- `rtk npm --prefix apps/desktop run build` passed with the existing Vite large-chunk warning.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_focuses.py tests/test_pihc3_migration_contracts.py` passed.
- In-app browser smoke check on `/e2e/diagram-apply-review-smoke.html` found 9 preview images at 40x40, no placeholders, no console warnings/errors, no horizontal overflow, and the review gate reporting the expected write/skip scope.

## Next

The C08_PARTIV focus-tree smoke now exercises source-focus layout metadata more closely. A useful next slice is to move from metadata-only focus updates toward per-source-folder `info.json` draft writes, so GUI edits can update the PIHC source folders directly when that source layer is present.
