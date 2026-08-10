# Diagram Unlock Edit Progress

Date: 2026-06-21 10:23

Linear: TAL-000

## Done

- Added an explicit selected-node `Add unlock` control for project diagrams, separate from the existing prerequisite control.
- Wired the desktop module editor to preserve the selected source node when creating or removing source-side unlock relationships.
- Updated the technology apply-review smoke fixture so source unlock edits produce the paired dependency/path-target draft expected by PIHC-style diagrams.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx src/styles/diagram.test.ts src/moduleEditor/diagramMetadata.test.ts src/diagramEditor/layoutModel.test.ts`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke: `http://127.0.0.1:5180/e2e/diagram-technology-apply-review-smoke.html` rendered compact actual image nodes, kept `TECHNOLOGY_LANDMINE` selected after `Add unlock TECHNOLOGY_FIREARM_I`, and produced writable metadata drafts without console warnings or errors.

## Risks Or Blockers

- The relationship editor is still a compact inspector form, not the final full HOI4-style graph editing workflow.

## Next

- Broaden source-side relationship editing into the main PIHC focus-tree smoke path and keep the command lane usable on normal Tauri window sizes.
