# Focus Move Smoke Progress

Date: 2026-06-21 02:59

Linear: TAL-000

## Done

- Updated `diagram-apply-review-smoke` to use 48 px focus slots, 1 x 1 focus nodes, direct migrated PIHC3 `focus_asset_component/.../preview.png` images, and dataset probes for grid/image verification.
- Removed the stale fake image bridge from the apply-review smoke so dummy pixels cannot satisfy the focus icon check.
- Added `diagram-move-smoke` for rendered coverage of move-subtree, move-node-only, and move-with-descendant-relayout behavior on a connected HOI4-style focus branch.
- Documented both smoke contracts in `apps/desktop/e2e/README.md`.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/layoutModel.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/projectDiagram.test.ts src/diagramEditor/diagramImages.test.ts src/styles/diagram.test.ts`
- `rtk git diff --check`
- `rtk npm --prefix apps/desktop run build`
- Browser QA:
  - `diagram-apply-review-smoke.html`: 9 preview PNG images, 0 placeholders, 48 px focus slots, 34 px images, apply review flow reaches `Apply calls: 1`.
  - `diagram-move-smoke.html`: 6 preview PNG images, 0 placeholders, subtree/node-only/relayout movement datasets match expected branch and descendant deltas, no console warn/error logs.

## Risks Or Blockers

- The movement smoke is a rendered fixture, not a packaged Tauri smoke; real project writes remain covered by the SDK/bridge tests and apply-review path.

## Next

- Continue tightening the normal in-app diagram tab so the same branch movement controls are ergonomic on large PIHC3 focus trees.
