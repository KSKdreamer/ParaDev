# 2026-06-21 00:14 - Focus Legacy Auto Offsets

## Context

The focus editor already moved toward square HOI4-style focus tiles, connected grid lines, branch dragging, and reflow previews. The remaining mismatch was PIHC/HOI4DEV legacy layout semantics: imported focuses with `parent` plus `dx/dy` were being treated as fixed relative-position nodes. In the legacy generator, `dx/dy` are auto-layout nudges applied after sibling packing, so the whole subtree follows the nudged focus while still participating in branch width and priority calculation.

## Changes

- Kept imported PIHC legacy `dx/dy` focuses in `auto` layout mode instead of converting them to fixed relative nodes.
- Marked those nodes as `legacy_offset` so the editor can still display and persist their stored offset fields.
- Preserved explicit `relative_position_id` as the real fixed-relative placement mode.
- Updated single-node movement so dragging a legacy auto-offset focus edits its `dx/dy` nudge and keeps descendants on the recalculated subtree.
- Updated metadata diff/writeback so changed legacy auto offsets create draft focus metadata instead of being ignored as plain auto-layout nodes.
- Updated selected-node coordinate badges and drag previews so legacy auto-offset focuses show both resolved grid coordinates and stored `dx/dy`.

## Verification

- Red checks:
  - `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/projectDiagram.test.ts` failed when the imported PIHC legacy focus still came in as `relative`.
  - `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/layoutModel.test.ts src/diagramEditor/projectDiagram.test.ts` failed when dragging a legacy offset node pinned it absolute instead of updating `dx/dy`.
  - `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx` failed before legacy auto-offset badges were included.
- Focused green:
  - `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/layoutModel.test.ts src/diagramEditor/projectDiagram.test.ts`
  - `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts`
  - `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
- Broader desktop checks:
  - `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/layoutModel.test.ts src/diagramEditor/projectDiagram.test.ts src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts src/diagramEditor/diagramHistory.test.ts src/diagramEditor/diagramImages.test.ts src/moduleEditor/diagramMetadata.test.ts src/moduleEditor/diagramSelection.test.ts src/moduleEditor/model.test.ts src/moduleEditor/ModuleEditor.test.tsx src/projectModules.test.ts src/styles/diagram.test.ts src/components/Workspace.test.tsx`
  - `rtk npm --prefix apps/desktop run test:unit`
  - `rtk npm --prefix apps/desktop run build`
- Browser QA at `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html` through the in-app browser:
  - Rendered 20 nodes, 10 edge paths, and 9 focus image or placeholder elements.
  - Selected focus showed resolved `x 5 y 5` and stored `dx -5 dy +5`.
  - Normal-window geometry had no horizontal overflow.
  - Console warning/error count was 0.

## Next

- Add a smoke fixture backed by actual PIHC legacy `parent` plus `dx/dy` data, not just the relative-position review fixture, so browser QA exercises the new auto-offset import path directly.
- Continue polishing branch movement controls around "move subtree as-is" versus "move focus and reflow descendants".
