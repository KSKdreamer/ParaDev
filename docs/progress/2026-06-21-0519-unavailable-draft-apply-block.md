# Unavailable Draft Apply Block Progress

Date: 2026-06-21 05:19

Linear: TAL-000

## Done

- Blocked diagram apply when any changed PIHC3 metadata row has a source path but no generated draft text.
- Kept the apply review visible so users can see the affected path and the generated-draft failure reason.
- Added localized disabled-state copy for unavailable generated drafts.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- ProjectDiagramView.test.tsx -t "skips PIHC3 metadata rows that have paths but no generated draft text"`
- `rtk npm --prefix apps/desktop run test:unit -- ProjectDiagramView.test.tsx ModuleEditor.test.tsx diagramMetadata.test.ts`
- `rtk npm --prefix apps/desktop run build`

## Risks Or Blockers

- The desktop build still emits the existing Vite large chunk warning.

## Next

- Continue tightening diagram apply behavior so generated review state and actual source edits cannot diverge.
