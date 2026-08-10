# PIHC3 provider-owned graph creation defaults

Date: 2026-07-31

## Done

- Added `ModuleDiagramSelectionDefault` to the public build-registry diagram
  contract. A provider can map fields from the selected node, apply a numeric
  offset, and render one `{value}` placeholder without family-specific desktop
  logic.
- Technology creation now inherits the selected folder and horizontal
  position, starts two rows below the selection, and initializes a dependency
  on it.
- Doctrine creation now starts two rows below the selection and initializes
  its project-owned hidden path/layout state.
- MIO organization creation now starts its first authored trait one row below
  the selected trait.
- The generic desktop module planner shows inherited advanced values, includes
  them in the reviewed dry plan, and reapplies them when the user changes the
  selected template. Older cached browser payloads remain compatible.
- PIHC3 technology, doctrine, and MIO extension templates own the corresponding
  resource fields. The technology template also no longer emits its
  description localization key twice.
- Regenerated the public build API reference at 118 symbols at the time of
  this slice and documented the
  selection-default extension contract in the architecture and authoring
  manuals.

## Real PIHC3 verification

- Provider-driven `write=False` plans succeeded for real selected Technology,
  Doctrine, and MIO nodes; no PIHC3 source module was created.
- Technology: 300 modules, 11,899 artifacts, zero diagnostics.
- Doctrine: 94 modules, 11,037 artifacts, zero diagnostics.
- MIO: 7 modules, 11,001 artifacts, zero diagnostics.
- The recursive source audit found zero `_component`, `_asset_component`,
  `legacy`, `inactive_modules`, or `__pycache__` paths.

## Regression gates

- 42 registry, diagram, and PIHC3 template integration tests passed.
- 2,166 fast Python tests passed; nine native-Windows tests were skipped.
- All 86 desktop test files and 1,412 tests passed.
- The strict TypeScript/Vite production build and changed Python source lint
  passed.
- Main-repository and PIHC3-repository diff integrity checks passed.

## Follow-up

The former MIO boundary is resolved by
`2026-07-31-pihc3-mio-trait-node-authoring.md`: the provider now owns a guarded
in-place trait and localization planner, and the public build API has grown to
121 symbols.
