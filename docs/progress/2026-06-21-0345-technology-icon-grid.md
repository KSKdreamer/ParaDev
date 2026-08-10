# Technology Icon Grid Progress

Date: 2026-06-21 03:45

Linear: TAL-000

## Done

- Changed technology diagrams to use 48 px grid slots and 1 x 1 icon nodes, matching the current HOI4-style focus-tree canvas direction.
- Rendered technology nodes through a compact image-only SVG branch with `.project-diagram-node.icon-node` and `.project-diagram-node-image.compact-icon`, without enabling focus-only insert/remove controls.
- Added a Vite smoke fixture for two PIHC3 technologies using real module-local `legacy/default.png` images through the mocked binary-source bridge.
- Updated stale focus metadata draft expectations to the current one-slot focus grid output.

## Verification

- `rtk npm --prefix apps/desktop run test:unit`
- `rtk npm --prefix apps/desktop run build`
- Browser smoke: `http://127.0.0.1:5180/e2e/diagram-technology-smoke.html` reported 2 compact icon nodes, 2 hydrated images, 48 px grid, 34 x 34 px image sizing, 0 placeholders, no node title/mode text, and no console warnings/errors.

## Risks Or Blockers

- Technology diagrams still use the module-local migrated source image, not generated `technology_asset_component/preview.png` files. That is usable with current PIHC3 data; asset-component preview generation remains a separate cleanup/migration improvement.

## Next

- Extend technology edit/apply review coverage so moved technology nodes draft back into the PIHC3 metadata path, mirroring the focus tree apply-review workflow.
