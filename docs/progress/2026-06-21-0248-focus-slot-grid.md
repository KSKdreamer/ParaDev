# Focus Slot Grid Progress

Date: 2026-06-21 02:48

Linear: TAL-000

## Done

- Changed project-browser focus diagrams to use a 48 px HOI4 focus-slot grid by default while preserving source `x`, `y`, `dx`, and `dy` values for metadata drafts.
- Switched default embedded focus nodes from 2 x 2 document grid units to 1 x 1 focus slots, keeping the rendered preview image at 34 x 34 px inside the same 48 x 48 px visual footprint.
- Added regression coverage that adjacent PIHC/HOI4 focus rows no longer overlap when source focuses use consecutive `y` values.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/projectDiagram.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/projectDiagram.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/diagramImages.test.ts src/styles/diagram.test.ts`
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k "focus_tree_preview_icons or focus_asset_component"`
- `rtk npm --prefix apps/desktop run build`
- `rtk git diff --check`
- Browser smoke at `http://127.0.0.1:5180/e2e/diagram-source-backed-smoke.html`: 6 focus nodes, 6 hydrated PNG images, 34 x 34 icon images, 48 x 48 focus slots, 0 placeholders, 0 legacy/default paths, 0 overlapping focus-node rectangles, no console warnings/errors.

## Risks Or Blockers

- The broader focus-tree editor still needs more branch manipulation and large-tree navigation polish; this checkpoint fixes the source-coordinate display spacing.

## Next

- Verify the source-backed rendered smoke page and keep improving branch movement/reflow ergonomics.
