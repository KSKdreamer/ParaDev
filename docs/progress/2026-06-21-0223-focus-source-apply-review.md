# Focus Source Apply Review Progress

Date: 2026-06-21 02:23

Linear: TAL-000

## Done

- Added apply-review rows for migrated focus source `legacy/<source_path>/info.json` files when a focus-tree diagram edit changes source-backed PIHC layout or relationship metadata.
- Kept module `meta.yaml` rows and migrated source JSON rows distinct even when they share the same focus-tree module id.
- Stabilized review-list row keys by changed entity id plus path so duplicate module ids can render together.
- Updated the apply-review smoke fixture to show two writable rows (`meta.yaml` and migrated `info.json`) plus one skipped row.

## Verification

- Red: `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/ModuleEditor.test.tsx -t "includes migrated focus source info files"` failed before the exported changed-entity builder existed.
- Green: same command passed after adding source-info changed rows.
- `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/ModuleEditor.test.tsx src/diagramEditor/ProjectDiagramView.test.tsx`.
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/projectDiagram.test.ts src/moduleEditor/diagramMetadata.test.ts`.
- `rtk npm --prefix apps/desktop run build`.
- Browser smoke at `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html` loaded without console warnings, rendered 9 PIHC3 focus preview images at `34 x 34` inside `48 x 48` focus nodes, and changed `Review scope first` to `Apply writable rows`.

## Risks Or Blockers

- The review count is file-row based, so a module and one migrated source file count as two writable rows.

## Next

- Continue tightening the full ModuleEditor/Tauri tab flow so the focus tree remains separate from ordinary module editing and is usable in a normal desktop window.
