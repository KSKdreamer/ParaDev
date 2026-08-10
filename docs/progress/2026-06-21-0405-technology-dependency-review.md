# Technology Dependency Review Progress

Date: 2026-06-21 04:05

Linear: TAL-000

## Done

- Made diagram dirty summaries always show writable and skipped counts, so all-writable multi-file PIHC3 edits are explicit before apply.
- Extended the technology apply-review smoke with a third real PIHC3 technology icon, `TECHNOLOGY_LANDMINE`.
- Verified adding `TECHNOLOGY_POWDER_EXPLOSIVE` as a prerequisite through the selected-node relationship controls, producing two reviewable metadata drafts:
  - `TECHNOLOGY_LANDMINE/meta.yaml` updates `dependency_ids`.
  - `TECHNOLOGY_POWDER_EXPLOSIVE/meta.yaml` updates `path_target_ids`.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit`
- `rtk git diff --check`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke: `http://127.0.0.1:5180/e2e/diagram-technology-apply-review-smoke.html` reported 3 compact icon nodes, 3 hydrated image nodes, 48 px grid, 34 x 34 px images, no placeholders, no console warnings/errors, one add-prerequisite candidate for Landmine, two dependency edges after adding Powder, two writable draft rows, dirty summary `Metadata drafts: 2 · Writable 2 · Skipped 0`, and clean state after the review/apply two-click flow.

## Risks Or Blockers

- The browser smoke uses the mocked Tauri binary-source bridge and in-memory apply callback. It verifies GUI behavior and metadata draft generation, but it does not write real PIHC3 files.

## Next

- Continue toward full tree-editor usability: make dependency/path edits easier to perform directly from the canvas, and add a proper in-app draft text/diff preview for metadata writes.
