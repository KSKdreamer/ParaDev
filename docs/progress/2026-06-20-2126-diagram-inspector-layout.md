# Diagram Inspector Layout

- Moved the selected-node inspector out of the SVG canvas overlay and into a diagram workspace beside the canvas.
- Kept the minimap inside the canvas while the inspector renders as a sibling panel, so focus icons and labels remain unobstructed.
- Added responsive stacking for narrower windows: the canvas stays first, and the inspector follows below it with natural row heights and scrollable workspace behavior.
- Added regressions for the markup boundary and CSS contract so the inspector does not drift back into an absolute canvas overlay.

Verification:

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx src/styles/diagram.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- src/components/Workspace.test.tsx src/moduleEditor/ModuleEditor.test.tsx src/diagramEditor/ProjectDiagramView.test.tsx src/diagramEditor/projectDiagram.test.ts src/diagramEditor/layoutModel.test.ts src/diagramEditor/diagramJson.test.ts src/moduleEditor/diagramMetadata.test.ts src/styles/diagram.test.ts`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke page at `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html?layout-hints=3`
- Browser probes confirmed the inspector is outside `.project-diagram-canvas`, right of the canvas at 1440x900, below the canvas at 1024x768, and has no console warnings.
- Interaction check filled the selected-node `priority` hint input and verified the live value changed to `21`.
- Screenshots: `/tmp/paradev-diagram-inspector-workspace-1440.png`, `/tmp/paradev-diagram-inspector-workspace-1024-final.png`
