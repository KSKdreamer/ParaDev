# Focus Source Legacy Offset Pin Cleanup Progress

Date: 2026-06-20 20:42

Linear: TAL-000

## Done

- Added a source-backed regression for pinning a migrated PIHC focus that still has legacy `parent` plus `dx`/`dy` offsets.
- Updated focus metadata position writeback so converting legacy offsets to absolute `x`/`y` also removes the stale `parent` key from `source_focuses`.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- src/components/Workspace.test.tsx src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts src/moduleEditor/diagramMetadata.test.ts`
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k focus_tree_importer_extracts_source_localization_and_image_metadata_contract`
- `rtk npm --prefix apps/desktop run build`
- Browser QA on `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html`: page identity matched, no console warnings/errors, no framework overlay, no horizontal overflow at 1440x900, zoom button changed state to 150%, selected focus node rendered an SVG focus image.

## Risks Or Blockers

- Desktop build still reports the existing Vite large-chunk warning.
- Worktree remains dirty with unrelated user and agent changes; this slice only reviewed the diagram metadata writer and regression.

## Next

- Continue normal-window focus-tree GUI QA and source-backed layout writeback cases for PIHC3 focus modules.
