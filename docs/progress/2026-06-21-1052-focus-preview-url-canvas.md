# Focus Preview URL Canvas Progress

Date: 2026-06-21 10:52

Linear: TAL-000

## Done

- Added PIHC3 focus-tree migration metadata for project-local focus asset previews via `source_focuses[*].preview_url`.
- Regenerated the PIHC3 migrated focus-tree modules so source-backed focuses point at `src/modules/focus_asset_component/*/preview.png`.
- Updated the desktop diagram adapter to prefer explicit source-focus preview URLs before falling back to inferred compiled focus asset paths.
- Kept focus image rendering compact at 34 px inside the 48 px focus grid, below a 2 x 2 grid footprint.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/projectDiagram.test.ts src/diagramEditor/diagramImages.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/styles/diagram.test.ts src/diagramEditor/sourceBackedSmokeModel.test.ts`
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k "focus_asset_component or focus_tree"`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_focuses.py tests/test_pihc3_migration_contracts.py`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke at `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html`: 9 focus nodes, 9 PNG-backed image nodes, 0 placeholders, 34 x 34 image size, 48 px grid, no horizontal overflow, and no console warnings or errors.

## Risks Or Blockers

- The focus-tree editor still needs broader UX hardening around large tree navigation, but the actual migrated image rendering path is now covered by unit, migration, and browser smoke checks.

## Next

- Continue tightening the source-backed focus editor around relationship edits, subtree movement, and apply-review confidence for larger PIHC3 trees.
