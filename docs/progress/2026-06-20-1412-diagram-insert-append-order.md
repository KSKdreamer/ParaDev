# 2026-06-20 14:12 - Diagram insert append order

## Slice

Made canonical diagram insertion append new child/root nodes after existing siblings when a caller supplies a colliding order.

## Changes

- Added layout-model regression tests for inserting a child and a root with requested `order: 0` while that order is already occupied.
- Updated child and root insertion to resolve the final order as `max(requestedOrder, nextAppendOrder)` when a finite requested order is present.
- Kept existing behavior for unordered inserts: they still use the next sibling/root append order.

## Verification

- Red check: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/layoutModel.test.ts -t "appends an inserted"` failed with both inserted nodes keeping `order: 0`.
- Green check: the same focused command passed with `2 passed`.
- Targeted suite: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/layoutModel.test.ts` passed with `44 passed`.
- Model/metadata suite: `rtk npm --prefix apps/desktop run test:model` passed with `120 passed`.
- Diagram view suite: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx` passed with `86 passed`.
- Frontend build: `rtk npm --prefix apps/desktop run build` passed; Vite still reports the existing large-chunk warning.

## Notes

- This keeps GUI-created focus/technology tree nodes from colliding with existing sibling/root order when PIHC3 metadata is regenerated.
