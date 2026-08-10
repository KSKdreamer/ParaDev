# PIHC3 Technology Registry Node Authoring

Date: 2026-08-02

## Outcome

The real PIHC3 Technology diagram no longer crashes on
`technology/PIHC_TECHNOLOGY_SUPPORT`. The project-local Technology provider now
owns the mixed source model explicitly: 300 modules with one `def` slot become
editable tree nodes, while the one no-`def` shared-source module remains a
first-class input to the same registered compiler.

Technology creation no longer hands the selected node to a separate module
template UI. The registered provider publishes a generic diagram-node form and
resolves it into `ModuleDiagramModuleCreation`, so the ordinary SDK, REST/MCP,
Tauri, and desktop diagram-edit path creates one minimal standalone module.
Only `def.txt` and preferred-language `main.loc` are required. Selection is
optional; when present it prefills folder, position, and prerequisite.

The provider binds current same-folder and prerequisite source revisions into
the reviewed plan hash. ParaDev then atomically installs the module, runs the
registered Technology family build, refreshes Catalog state only on success,
and removes the complete folder on build rejection.

## Architecture audit

- MIO already uses the generic Registry-owned in-place node planner and keeps
  its Entity/compiler project-local.
- Doctrine remains intentionally source-authoritative for creation because its
  current visual positions are imported summaries; no metadata-only creation
  path was added.
- ParaDev core and the built-in HoI4 Technology provider retain their generic
  one-definition contract. PIHC3-specific support-module semantics exist only
  in the PIHC3 extension.

## Verification

- Complete Python gate: 2,496 passed, with nine expected native-Windows-only
  skips.
- Affected Technology/diagram/Focus/MIO gates passed, including dry planning,
  minimal creation, exact apply, duplicate rejection, stale-tree rejection,
  build-rejection rollback, and the live 300-node PIHC3 projection.
- Desktop: 89 files and 1,453 tests passed; strict TypeScript/Vite production
  build and Rust `cargo check` passed.
- Strict artifact-emitting PIHC3 builds remained unblocked with zero
  diagnostics/errors:
  - clean/full and cached/full: 14,617 modules, 106 collections, 35,131
    artifacts;
  - Technology family: 301 modules, 11,901 artifacts;
  - `technology/TECHNOLOGY_CANNON_HEAVY_CONTEMPORARY`: one module, 10,997
    artifacts.
- The live physical audit again found no `_component`, `_asset_component`,
  `legacy`, `inactive_modules`, symlinked module, or module folder without the
  `id - preferred localization` shape.

## Remaining work

- Continue tree UX and source-authoritative authoring work without adding
  family switches to React or the generic SDK.
- Doctrine creation should move in-place only after its canonical compiled PDX
  owns trustworthy layout/path writeback; until then its diagram remains
  intentionally view-only.
- Native Windows integration and macOS game launching remain outside the
  current priority.
