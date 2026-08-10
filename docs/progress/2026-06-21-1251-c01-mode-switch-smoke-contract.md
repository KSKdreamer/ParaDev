# C01 Mode Switch Smoke Contract Progress

Date: 2026-06-21 12:51

## Done

- Added diagram-tab smoke dataset fields for selected focus node id, selected node mode, visible mode-switch count, visible switch mode, and selected/switch match.
- Wired the C01 `diagram-tab-smoke.html` fixture to derive selected node mode from the rendered SVG node and compare it with the upper-right mode switch state.
- Updated the desktop E2E fixture README to require the C01 selected-node switch cycle through auto, relative, pinned, and back to auto.

## Verification

- `rtk npm --prefix apps/desktop exec vitest run e2e/diagram-tab-smoke-state.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/styles/diagram.test.ts`
- `rtk npm --prefix apps/desktop run build`
- `rtk npm --prefix apps/desktop exec vitest run e2e/diagram-tab-smoke-state.test.ts`
- Browser smoke at `http://127.0.0.1:5180/e2e/diagram-tab-smoke.html`: opened the National Focuses diagram tab, confirmed C01_MAIN `83/83` hydrated images, selected `FOCUS_C01_COZY_GLOW_CORONATION`, then clicked the upper-right mode switch through `auto -> relative -> absolute -> auto` with `data-paradev-diagram-tab-smoke-mode-switch-selected-match="1"` throughout.

## Next

- Keep hardening C01 source-backed position edits so the GUI state, review rows, and generated `legacy/<focus>/info.json` drafts stay visibly tied together.
