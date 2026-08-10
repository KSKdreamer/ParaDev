# 2026-06-20 11:47 - Diagram Reparent Position Preservation

## Scope

Tightened focus-tree and technology-tree relationship editing so tree-parent changes do not unexpectedly move nodes or create invalid parentless relative nodes.

## Changes

- Reparenting a non-absolute node now preserves its resolved world position by storing a new parent-relative offset.
- Clearing the parent of a relative or auto node now promotes it to an absolute pinned root at the same resolved world position.
- Absolute nodes keep their existing pinned coordinates when their tree parent changes.

## Verification

- Red test first: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/layoutModel.test.ts` failed on reparenting an auto child because it stayed auto under the new parent.
- Focused green: the same layout suite passed after preserving the reparented node position.
- Second red test: the same layout suite failed when clearing a relative parent left a root-level relative node.
- Second focused green: the same layout suite passed after pinning promoted non-absolute roots.
- Third red test: the same layout suite failed when clearing an auto parent left a root-level auto node that would visually move.
- Third focused green: the same layout suite passed after generalizing promoted-root pinning.
- Adjacent diagram suites passed:
  - `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/projectDiagram.test.ts src/diagramEditor/ProjectDiagramView.test.tsx`
  - `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts`
  - `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramHistory.test.ts src/diagramEditor/diagramJson.test.ts src/diagramEditor/diagramJsonImport.test.ts`
- Full desktop unit suite: `rtk npm --prefix apps/desktop run test:unit` passed.
- Desktop build: `rtk npm --prefix apps/desktop run build` passed with the existing Vite large chunk warning.

## Notes

This keeps relationship edits aligned with the editor design principle that layout only changes through explicit layout commands. It also protects PIHC3 focus edits from creating metadata-backed diagram states that cannot resolve after a parent is cleared.
