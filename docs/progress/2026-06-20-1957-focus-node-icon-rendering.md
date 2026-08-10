# Focus Node Icon Rendering

## Summary

Made embedded focus-tree nodes render as compact icon-first nodes while keeping normal diagram nodes on the existing label-card layout.

## Changes

- Split focus-node SVG rendering from generic diagram-node rendering in `ProjectDiagramView`.
- Centered focus images inside focus nodes with `preserveAspectRatio="xMidYMid meet"` and a bottom-centered focus label.
- Added focus-node CSS styling and regression coverage for embedded focus image nodes and local PIHC-style image hydration.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/ProjectDiagramView.test.tsx`
- `rtk npm --prefix apps/desktop run test:unit -- src/diagramEditor/projectDiagram.test.ts`
- `rtk npm --prefix apps/desktop run build`
- Browser QA on `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html?toolbar-groups=1`:
  - 1440x900: two `.project-diagram-node.focus-node` nodes rendered, selected root focus hydrated its image from the mocked PIHC path, image attributes were `width=30`, `height=30`, `x=33`, `y=7`, and page overflow was `0`.
  - 1024x768: focus nodes stayed inside the panel, the icon and centered label remained stable, and page overflow was `0`.
  - Review/apply interaction: clicked through review confirmation and apply; smoke state changed to `Apply calls: 1` and `Clean`.
  - Console warnings/errors: none.
