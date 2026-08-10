# Diagram Toolbar Command Lane Progress

Date: 2026-06-21 10:04

Linear: TAL-000

## Done

- Kept the selected-node diagram toolbar controls in a single compact horizontal lane instead of letting the move/action strip wrap into extra toolbar rows.
- Added a style contract so `.project-diagram-node-tools` clips its own lane and `.project-diagram-nudge` / `.project-diagram-move-tools` stay `nowrap` with horizontal overflow available.
- Preserved the existing focus image canvas behavior while tightening the command surface around branch/node-only/reflow movement modes.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/styles/diagram.test.ts src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke at `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html`: page identity correct, app snapshot present, no console warnings/errors, move-mode interaction switched `Node only` to `aria-pressed=true`, then restored `Branch`.
- Browser metrics: 1023 x 1011 viewport had 0 body horizontal overflow, 9 focus images, 0 focus placeholders, `Images 9/9`; 820 x 760 and 700 x 760 stress viewports kept the selected-node command lane to 29 px height with `flex-wrap: nowrap`.

## Risks Or Blockers

- The global diagram toolbar still wraps into multiple rows at narrow widths because search, viewport, file, status, and apply-review groups are all visible. This slice only prevents selected-node controls from adding more vertical wrapping.

## Next

- Consider a grouped/overflow menu for lower-frequency global diagram actions if normal-window header height remains too tall in real Tauri windows.
