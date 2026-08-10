# 2026-06-20 14:20 - Diagram technology selection facts

## Slice

Cleaned up technology-tree selection-panel facts and dependency candidate safety.

## Changes

- Added a render regression test for technology nodes so their module item id no longer appears under a focus-tree label.
- Updated selection facts to keep `Focus tree` only for embedded focus nodes and use a generic `Item` label for non-focus diagram items.
- Added English and Chinese locale entries for the new item label.
- Added a render regression test that prevents outgoing unlock nodes from being offered as new prerequisites, avoiding reciprocal dependency edits in focus/technology diagrams.
- Updated dependency edit candidates to exclude both existing prerequisites and existing unlocks.

## Verification

- Red check: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx -t "technology module facts"` failed with `Focus tree` shown for `technology:TECH_FIREARM`.
- Green check: the same focused command passed with `1 passed`.
- Red check: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx -t "selected unlocks"` failed because `NEXT` was offered as a prerequisite candidate.
- Green check: the same focused command passed with `1 passed`.
- Diagram view suite: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx` passed with `88 passed`.
- Model/metadata suite: `rtk npm --prefix apps/desktop run test:model` passed with `121 passed`.
- Desktop unit suite: `rtk npm --prefix apps/desktop run test:unit` passed with `302 passed`.
- Frontend build: `rtk npm --prefix apps/desktop run build` passed; Vite still reports the existing large-chunk warning.

## Notes

- This improves technology-tree usability without pretending technology modules are embedded focus records, and keeps PIHC3 dependency/path edits from suggesting reciprocal prerequisite links.
