# Focus Image Size Contract Progress

Date: 2026-06-21 04:59 +0800

Linear: TAL-000

## Done

- Exported the diagram canvas image-size helper used by rendered focus and technology nodes.
- Removed the duplicated PIHC3 smoke-fixture focus image formula so the fixture reads the same sizing contract as the canvas.
- Added a focused regression check that PIHC focus preview images render at `34px` on the `48px` grid and remain below a `2 x 2` grid footprint.

## Verification

- `rtk npm --prefix apps/desktop run test:unit -- ProjectDiagramView.test.tsx diagramImages.test.ts projectDiagram.test.ts`
- `rtk npm --prefix apps/desktop run test:unit -- App.test.ts AppShell.test.tsx nativeProgress.test.ts`
- Browser smoke at `http://127.0.0.1:5180/e2e/diagram-apply-review-smoke.html`: 9 PIHC3 `preview.png` focus images, 0 legacy fallback images, expected SVG image size `34`, grid `48`, all images below `2 x 2`.
- `rtk npm --prefix apps/desktop run build`
- `rtk git diff --check -- apps/desktop/src/diagramEditor/ProjectDiagramView.tsx apps/desktop/src/diagramEditor/ProjectDiagramView.test.tsx apps/desktop/e2e/diagram-apply-review-smoke.tsx`

## Risks Or Blockers

- The production build still reports Vite's existing large-chunk warning, but TypeScript and the build completed successfully.

## Next

- Continue tightening the focus/technology editor around PIHC3 source-backed apply behavior and tree movement ergonomics.
