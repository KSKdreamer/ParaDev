# 2026-06-20 11:32 - Focus Relative Position Metadata

## Scope

Fixed a PIHC3 focus-tree round-trip gap in the desktop diagram editor metadata writer. Switching a focus node to relative coordinate mode now writes `relative_position_id`, and pinning or auto-layouting out of relative mode removes that scalar.

## Changes

- Added regression coverage for making a PIHC3 focus child relative from absolute coordinates.
- Added regression coverage for pinning a PIHC3 relative focus back to absolute coordinates.
- Extended diagram metadata change detection to compare focus relative-position state.
- Reused the existing scalar YAML updater so `relative_position_id` follows the current indentation and quoting behavior.

## Verification

- Red test first: `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts -t "relative positioning metadata"` failed on missing/stale `relative_position_id`.
- Focused green: same command passed after implementation.
- Metadata suite: `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts` passed.
- Diagram suites: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/layoutModel.test.ts src/diagramEditor/projectDiagram.test.ts src/diagramEditor/ProjectDiagramView.test.tsx` passed.
- Full desktop unit suite: `rtk npm --prefix apps/desktop run test:unit` passed.
- Desktop build: `rtk npm --prefix apps/desktop run build` passed with the existing Vite large chunk warning.
- Whitespace check: `rtk git diff --check -- apps/desktop/src/moduleEditor/diagramMetadata.ts apps/desktop/src/moduleEditor/diagramMetadata.test.ts` passed for tracked changes; these diagram files are currently untracked in the worktree.

## Notes

This keeps the relative-mode UI command aligned with PIHC3 metadata semantics. Without this, a focus node could look relative in the editor draft but reload as absolute after Apply.
