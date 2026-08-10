# Stable Version Final Sync Progress

Date: 2026-06-21 00:54

Linear: N/A

## Done

- Wrapped the stable checkpoint after the API catalog, CLI selector, and desktop focus-tree editor slices.
- Kept active legacy migration references because the docs menu still routes migration agents through them as current evidence.
- Removed the empty untracked `docs/requests/` artifact instead of carrying request scratch space into the stable tree.
- Included the focus-tree editor's compact icon tile and PIHC source-layout preservation changes in the final whole-repo commit scope.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts src/diagramEditor/projectDiagram.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/layoutModel.test.ts`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -k focus_tree_importer -q`
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -k focus_asset_component -q`
- `rtk bash scripts/sync-readme.bash --check`
- `rtk bash scripts/flake.bash --ci`
- `rtk git diff --check`

## Risks Or Blockers

- The focus-tree editor is intentionally still evolving; this checkpoint stabilizes the current compact icon and layout-writeback behavior without declaring the editor complete.
- Full repo tests were not run to avoid unnecessary CPU churn; focused Python contracts plus full desktop unit/build, docs sync, and lint gates cover the committed surface.

## Next

- Continue the focus-tree editor in small slices, with per-source-folder `info.json` draft writes as the next useful direction.
