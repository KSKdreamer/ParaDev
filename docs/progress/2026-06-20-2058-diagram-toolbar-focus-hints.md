# Diagram Toolbar And Focus Hints

- Kept the dedicated diagram toolbar readable at normal desktop widths by preventing diagram action groups and buttons from shrinking into stacked labels; the toolbar now scrolls horizontally when the window is narrow.
- Exposed PIHC legacy focus layout hints in the selected-node facts: `priority`, lane width (`w`/`pw`), lane delta (`dw`), and center offset (`dc`).
- Adjusted icon-first focus nodes so the icon image has its own lane and the label renders below it instead of through the image.
- Added regressions for the toolbar CSS contract and selected-node legacy layout hints.

Verification:

- `rtk npm --prefix apps/desktop run test:unit -- src/components/Workspace.test.tsx src/moduleEditor/ModuleEditor.test.tsx src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts src/moduleEditor/diagramMetadata.test.ts src/styles/diagram.test.ts`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke page at `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html?toolbar-groups=1&codex=2057`
- Screenshots: `/tmp/paradev-diagram-toolbar-normal-window-after-icon.png`, `/tmp/paradev-diagram-toolbar-1024-after-icon.png`
