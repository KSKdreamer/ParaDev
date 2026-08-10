# Focus Layout Alias Cleanup Progress

Date: 2026-06-21 05:10

Linear: TAL-000

## Done

- Canonicalized migrated PIHC source focus layout-hint writes so accepted long-form aliases do not remain beside `w`, `dw`, and `dc`.
- Preserved existing `pw` width style when it is the active legacy key, while removing stale width aliases.
- Added a regression that updates both `source_focuses` YAML and `legacy/<focus>/info.json` from alias-heavy layout fields.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- diagramMetadata.test.ts -t "canonicalizes migrated PIHC source focus layout aliases when layout hints change"`
- `rtk npm --prefix apps/desktop run test:unit -- diagramMetadata.test.ts projectDiagram.test.ts layoutModel.test.ts`
- `rtk npm --prefix apps/desktop run build`

## Risks Or Blockers

- The desktop build still emits the existing Vite large chunk warning.

## Next

- Continue reducing ambiguity in PIHC3 focus-source writeback and apply-review behavior before broad cleanup.
