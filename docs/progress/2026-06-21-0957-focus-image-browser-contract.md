# Focus Image Browser Contract Progress

Date: 2026-06-21 09:57

Linear: TAL-000

## Done

- Rechecked the source-backed PIHC3 focus image path from migrated `src/modules/focus_asset_component/*/preview.png` records through Tauri-style binary-source hydration and SVG canvas rendering.
- Confirmed the C08_PARTIV smoke renders actual `<image class="project-diagram-node-image focus-icon">` nodes instead of placeholders.
- Confirmed the rendered focus tiles are 48 x 48 px grid slots with 34 x 34 px images at x/y 7, keeping each icon smaller than a 2 x 2 focus grid footprint.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramImages.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/sourceBackedSmokeModel.test.ts`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke at `http://127.0.0.1:5180/e2e/diagram-source-backed-smoke.html`: 9 focus image nodes, 0 focus placeholders, `Images 9/9`, 9 binary-source reads, last read path `src/modules/focus_asset_component/FOCUS_ASSET_COMPONENT_FOCUS_C08_PLAN_TWILIGHT/preview.png`.

## Risks Or Blockers

- The source-backed smoke covers C08_PARTIV. Broader PIHC3 trees still need more fixtures if their source metadata uses image naming or layout aliases not present in C08.

## Next

- Continue normal-window polish for the focus-tree toolbar/canvas and add broader PIHC3 source-backed fixture coverage when new layout/image aliases appear.
