# Diagram Popup Smoke Contract Progress

Date: 2026-06-21 12:46

## Done

- Added a small diagram-tab smoke state helper that writes opened focus-node popup state into stable HTML dataset fields.
- Wired `diagram-tab-smoke.html` to expose popup count, aria label, focus node id, title, source-info path, and selected-node match after a real double-click.
- Updated the desktop E2E fixture README with the C01 popup dataset verification step.

## Verification

- `rtk npm --prefix apps/desktop exec vitest run e2e/diagram-tab-smoke-state.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/styles/diagram.test.ts`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke at `http://127.0.0.1:5180/e2e/diagram-tab-smoke.html`: opened the separate National Focuses diagram tab, confirmed C01_MAIN `83/83` hydrated images, then double-clicked `FOCUS_C01_DEM_CHANGE` and verified `data-paradev-diagram-tab-smoke-popup-node-id="FOCUS_C01_DEM_CHANGE"`, `data-paradev-diagram-tab-smoke-popup-selected-match="1"`, and `data-paradev-diagram-tab-smoke-popup-source-info-path="src/modules/focus_tree/C01_MAIN/legacy/C01_DEM_CHANGE/info.json"`.

## Next

- Continue hardening focus-tree editing around direct node actions and reduce remaining diagram-page chrome where it does not serve normal PIHC migration workflows.
