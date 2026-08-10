# Diagram Narrow Global Actions Progress

Date: 2026-06-21 10:09

Linear: TAL-000

## Done

- Added explicit `aria-label` and `title` attributes to diagram export/import and whole-diagram layout buttons so they remain accessible when compacted.
- Added a narrow-window media rule that turns low-frequency global diagram actions into 26 px icon-only buttons under 860 px, while keeping review/apply status text visible.
- Preserved the existing selected-node command lane and PIHC3 focus image canvas behavior.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/styles/diagram.test.ts src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke at `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html`: page identity correct, app snapshot present, no framework overlay, no console warnings/errors.
- Browser 820 x 760: export and auto-layout buttons measured 26 x 26 px with `font-size: 0`, review/apply stayed visible, export button opened the JSON panel.
- Browser 700 x 760: toolbar had 0 body horizontal overflow, 9 focus images, 0 focus placeholders, `Images 9/9`, and the canvas started at y=250 versus the previous y=287 stress measurement.

## Risks Or Blockers

- The toolbar still uses wrapping for primary groups. A future pass should consider a structured overflow menu for rarely used JSON/layout actions once the main focus-tree interactions stabilize.

## Next

- Continue reducing toolbar noise around focus-tree editing, especially lower-frequency JSON/import actions and relationship editing commands.
