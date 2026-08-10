# 2026-06-20 11:55 - Relative Focus Parent Cleanup

## Scope

Tightened PIHC3 focus-tree metadata drafts for relative focus edits. When a focus uses `relative_position_id`, that scalar now owns the visual parent and the draft writer removes redundant `parent` metadata instead of persisting both parent sources.

## Changes

- Added regression coverage for reparenting a relative focus while preserving its world position as recalculated relative offsets.
- Added regression coverage for converting an already-parented absolute focus to relative positioning without leaving stale `parent` metadata.
- Updated the focus relative-position scalar writer to clear `parent` only when writing a non-empty `relative_position_id`, so pinning back to absolute mode can still keep normal parent metadata when present.

## Verification

- Red tests first: `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts -t "relative focus reparenting|parent metadata"` failed on redundant `parent` metadata.
- Focused green: same command passed after implementation.
- Metadata suite: `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts` passed.
- Related diagram suites: `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/layoutModel.test.ts src/diagramEditor/projectDiagram.test.ts src/diagramEditor/ProjectDiagramView.test.tsx` passed.
- Full desktop unit suite: `rtk npm --prefix apps/desktop run test:unit` passed.
- Desktop build: `rtk npm --prefix apps/desktop run build` passed with the existing Vite large-chunk warning.
- Whitespace checks: `rtk git diff --check -- apps/desktop/src/moduleEditor/diagramMetadata.ts apps/desktop/src/moduleEditor/diagramMetadata.test.ts docs/progress/2026-06-20-1155-relative-focus-parent-cleanup.md` passed; because these files are currently untracked, `rtk perl -ne 'print "$ARGV:$.:$_" if /[ \t]$/ || /\r$/; close ARGV if eof' apps/desktop/src/moduleEditor/diagramMetadata.ts apps/desktop/src/moduleEditor/diagramMetadata.test.ts docs/progress/2026-06-20-1155-relative-focus-parent-cleanup.md` was also run and produced no output.
