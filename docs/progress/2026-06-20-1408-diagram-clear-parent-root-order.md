# 2026-06-20 14:08 - Diagram clear-parent root order

## Slice

Made canonical diagram parent clearing append promoted nodes after existing roots when their old child order would collide.

## Changes

- Added a layout-model regression test for clearing `child` from `old-parent` while another root already exists.
- Updated `clearDiagramTreeParent` to set promoted root order to `max(oldOrder, nextRootOrder)`.
- Preserved the existing visual-position contract: relative and auto nodes are still pinned to their resolved world position when promoted to roots.

## Verification

- Red check: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/layoutModel.test.ts -t "appends a cleared child"` failed with `order: 0` instead of `order: 2`.
- Green check: the same focused command passed with `1 passed`.
- Targeted suite: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/layoutModel.test.ts` passed with `42 passed`.
- Model/metadata suite: `rtk npm --prefix apps/desktop run test:model` passed with `118 passed`.

## Notes

- This keeps focus-tree root promotion deterministic when a PIHC3 focus is detached from its parent through the GUI.
