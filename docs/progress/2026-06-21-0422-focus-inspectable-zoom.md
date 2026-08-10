# Focus Inspectable Zoom Progress

Date: 2026-06-21 04:22

Linear: TAL-000

## Done

- Added document-aware initial zoom for image-backed compact focus/technology diagrams so large PIHC3 focus trees open at an inspectable close-up instead of a whole-tree fit.
- Preserved saved viewport JSON as the source of truth; explicit viewport zoom/pan still restores exactly.
- Added a ProjectDiagramView regression that checks image-backed focus nodes open at 200% with 34 px icon slots and that saved 100% viewport state wins.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/projectDiagram.test.ts src/diagramEditor/diagramImages.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/ModuleEditor.test.tsx`
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'focus_asset_component or focus_tree_preview_icons_resolve'`
- `rtk npm --prefix apps/desktop run build`
- `rtk git diff --check`
- Browser smoke `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html`: 9 real focus images, 0 placeholders, 34 x 34 SVG image slots, rendered about 39 x 39 px at 200% in the normal window.

## Risks Or Blockers

- Production build still reports the existing Vite large-chunk warning.
- This improves initial readability; deeper HOI4-style branch navigation still needs richer viewport commands and canvas-scale UX.

## Next

- Add a source-backed large-tree smoke for the full PIHC3 focus tree, not only the compact C08 fixture.
- Continue PIHC3 folder cleanup and one-command build verification.
