# Diagram Tab Source-Backed Images Progress

Date: 2026-06-21 07:15

Linear: TAL-000

## Done

- Switched the separate diagram-tab smoke from a two-node inline data URL fixture to the shared source-backed PIHC3 `C08_PARTIV` fixture.
- Extracted the C08 focus preview binary-source bridge into a reusable e2e helper so both the direct `ProjectDiagramView` smoke and the shell diagram-tab smoke hydrate migrated `focus_asset_component/.../preview.png` images the same way.
- Added diagram-tab smoke dataset counters for preview node count, hydrated focus images, placeholders, image status, binary reads, and cache writes.

## Verification

- `rtk npm run test:unit -- src/diagramEditor/sourceBackedSmokeModel.test.ts src/diagramEditor/diagramImages.test.ts src/components/Workspace.test.tsx src/components/AppShell.test.tsx src/App.test.ts`
- `rtk npm run build`
- Browser QA: `diagram-tab-smoke.html` opens `diagram:focuses` with 9 focus images, 0 placeholders, `Images 9/9`, 9 binary reads, and 9 thumbnail cache writes.
- Browser QA: `diagram-source-backed-smoke.html` still reports 9 focus images, 0 placeholders, `Images 9/9`, 9 binary reads, and 9 thumbnail cache writes after the bridge helper extraction.

## Risks Or Blockers

- Vite still reports the existing large-chunk warning.
- The broad GUI editor still needs normal-app end-to-end coverage against a live Tauri backend, not only e2e browser bridge fixtures.

## Next

- Keep closing the gap between smoke-page coverage and the normal packaged Tauri workflow for PIHC3 diagram edits.
