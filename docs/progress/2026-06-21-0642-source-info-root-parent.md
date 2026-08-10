# Source Info Root Parent Progress

Date: 2026-06-21 06:42

Linear: TAL-000

## Done

- Added regression coverage for clearing a migrated PIHC focus visual parent when the editable source is the per-focus `legacy/<focus>/info.json` file.
- Changed source-info JSON writeback so clearing a source-backed focus parent writes `"parent": null` instead of deleting the key.
- This preserves an explicit source root after refresh, so prerequisite edges do not get reinterpreted as tree parents by the source-backed diagram adapter.

## Verification

- `rtk npm run test:unit -- src/moduleEditor/diagramMetadata.test.ts`
- `rtk npm run test:unit -- src/moduleEditor/diagramMetadata.test.ts src/moduleEditor/ModuleEditor.test.tsx src/diagramEditor/projectDiagram.test.ts src/diagramEditor/sourceBackedSmokeModel.test.ts src/diagramEditor/layoutModel.test.ts`
- `rtk npm run build`

## Risks Or Blockers

- None for this slice. Source-info writeback still needs broader browser-level apply coverage for real drag/clear-parent flows.

## Next

- Add rendered diagram apply smoke coverage for clearing a source-backed focus parent and applying the generated source-info JSON draft.
