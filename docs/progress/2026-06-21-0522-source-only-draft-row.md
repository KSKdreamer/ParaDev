# Source-Only Draft Row Progress

Date: 2026-06-21 05:22

Linear: TAL-000

## Done

- Dropped unchanged module `meta.yaml` rows from diagram apply review when only a migrated PIHC3 source-info draft is generated.
- Preserved unavailable-draft blocking for missing source-info rows so incomplete PIHC3 writes still cannot be partially applied.
- Added a regression for source-only `legacy/<focus>/info.json` draft rows.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- ModuleEditor.test.tsx -t "drops unchanged PIHC3 meta rows when only a source info draft is generated"`
- `rtk npm --prefix apps/desktop run test:unit -- ModuleEditor.test.tsx ProjectDiagramView.test.tsx diagramMetadata.test.ts`
- `rtk npm --prefix apps/desktop run build`

## Risks Or Blockers

- The desktop build still emits the existing Vite large chunk warning.

## Next

- Continue aligning diagram apply review rows with the exact source edits generated for PIHC3 focus trees.
