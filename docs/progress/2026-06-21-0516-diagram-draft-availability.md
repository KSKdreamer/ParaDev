# Diagram Draft Availability Progress

Date: 2026-06-21 05:16

Linear: TAL-000

## Done

- Added explicit unavailable-draft state for PIHC3 diagram metadata rows whose source path exists but no generated draft text is available.
- Updated the diagram dirty scope and apply review so those rows remain visible with their paths but count as skipped, not writable.
- Added regressions for both the changed-row builder and rendered apply-review summary.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- ModuleEditor.test.tsx ProjectDiagramView.test.tsx -t "marks changed PIHC3 rows without generated draft text as unavailable|skips PIHC3 metadata rows that have paths but no generated draft text"`
- `rtk npm --prefix apps/desktop run test:unit -- ModuleEditor.test.tsx ProjectDiagramView.test.tsx diagramMetadata.test.ts projectDiagram.test.ts layoutModel.test.ts`
- `rtk npm --prefix apps/desktop run build`

## Risks Or Blockers

- The desktop build still emits the existing Vite large chunk warning.

## Next

- Continue hardening PIHC3 source-backed apply behavior so review scope always matches actual source edits.
