# Focus Layout Control Isolation Progress

Date: 2026-06-21 05:05

Linear: TAL-000

## Done

- Hid the PIHC legacy layout-hint editor from selected technology nodes so focus-tree-only controls stay isolated to embedded focus diagrams.
- Updated the editable-layout-hint focus fixture to use the same embedded focus payload shape as migrated PIHC3 focus-tree nodes.
- Added a regression test that proves technology diagrams can receive the shared diagram editor handlers without exposing `priority`, `w`, `dw`, or `dc` focus controls.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- ProjectDiagramView.test.tsx -t "hides PIHC legacy layout hint controls for selected technology nodes"`
- `rtk npm --prefix apps/desktop run test:unit -- ProjectDiagramView.test.tsx projectDiagram.test.ts layoutModel.test.ts diagramImages.test.ts`
- `rtk npm --prefix apps/desktop run build`

## Risks Or Blockers

- The desktop build still emits the existing Vite large chunk warning for current bundle shape.

## Next

- Continue tightening focus-tree-specific actions and writeback review around migrated PIHC3 focus source files.
