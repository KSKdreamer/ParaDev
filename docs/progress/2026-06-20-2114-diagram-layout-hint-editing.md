# Diagram Layout Hint Editing

- Added editable PIHC legacy layout hint controls to the selected focus-node inspector: `priority`, lane width (`w`/`pw`), lane delta (`dw`), and center offset (`dc`).
- Added a diagram model setter for layout hints so the GUI can update draft focus metadata without mixing the behavior into drag positioning.
- Wired migrated PIHC focus-tree writeback to update `source_focuses` first, preserving existing `pw`/`w` width style where possible and clearing optional hints when the user blanks them.
- Updated the diagram apply-review smoke fixture so normal-window browser QA covers visible focus icons plus editable PIHC layout hints.

Verification:

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/layoutModel.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/moduleEditor/diagramMetadata.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- src/components/Workspace.test.tsx src/moduleEditor/ModuleEditor.test.tsx src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/diagramJson.test.ts src/moduleEditor/diagramMetadata.test.ts src/styles/diagram.test.ts`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke page at `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html?layout-hints=2`
- Screenshots: `/tmp/paradev-diagram-layout-hints-final-1440.png`, `/tmp/paradev-diagram-layout-hints-final-1024.png`
