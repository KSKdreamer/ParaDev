# Focus Source Relationship Drafts Progress

Date: 2026-06-21 02:14

Linear: TAL-000

## Done

- Extended migrated focus `legacy/<source_path>/info.json` drafts to relationship edits from the focus-tree editor.
- Canonicalized edited dependency sources into `prerequisites` lists and mutual-exclusion targets into `mutually_exclusive` lists.
- Removed legacy dependency aliases such as singular `prerequisite` and `prerequisite__D*` when a GUI relationship edit writes the source JSON.

## Verification

- Red: `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts -t "updates migrated PIHC source focus info json relationships"` failed because only the `meta.yaml` draft was produced.
- Green: same command passed after adding source JSON relationship writes.
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/projectDiagram.test.ts src/moduleEditor/diagramMetadata.test.ts`.
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/diagramImages.test.ts src/diagramEditor/ProjectDiagramView.test.tsx src/moduleEditor/ModuleEditor.test.tsx`.
- `rtk npm --prefix apps/desktop run build`.

## Risks Or Blockers

- The source writer emits ParaDev canonical list fields instead of trying to preserve every PIHC2 relationship alias in edited files.

## Next

- Add browser-level coverage for apply-review rows that include both `meta.yaml` and source `info.json` edits.
