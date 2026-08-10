# Source Picker Smoke Contract Progress

Date: 2026-06-21 14:25

Linear: TAL-000

## Done

- Added diagram-tab smoke dataset fields for the compact module source picker, selected source value/text, selected source path readout, compact source-tab count, and source editor visibility.
- Wired the rendered `diagram-tab-smoke.html` fixture to report the source picker state from the real module editor DOM.
- Kept the change as a smoke-observability slice only; the module editor UI behavior remains unchanged.

## Verification

- Red test first: `rtk npm --prefix apps/desktop exec vitest run e2e/diagram-tab-smoke-state.test.ts` failed because `writeDiagramTabSmokeSourceDataset` did not exist.
- `rtk npm --prefix apps/desktop exec vitest run e2e/diagram-tab-smoke-state.test.ts`
- `rtk npm --prefix apps/desktop exec vitest run e2e/diagram-tab-smoke-state.test.ts src/moduleEditor/ModuleEntityDetails.test.tsx src/moduleEditor/ModuleEditor.test.tsx`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke at `http://127.0.0.1:5180/e2e/diagram-tab-smoke.html`: opened National Focuses, selected `focus:FOCUS_C01_DEM_CHANGE:info` in the compact source picker, confirmed `src/modules/focus_tree/C01_MAIN/legacy/C01_DEM_CHANGE/info.json`, two compact source tabs, source editor visible, and no console warnings/errors.

## Risks Or Blockers

- The in-app browser SVG click path still hit the diagram pan surface in this session, so browser verification covered the rendered module editor source picker directly rather than the double-click popup handoff.
- The production build still emits the existing Vite large-chunk warning.

## Next

- Continue tightening browser automation around diagram-node hit testing and popup-to-module handoff now that the module-side source picker state is machine-readable.
