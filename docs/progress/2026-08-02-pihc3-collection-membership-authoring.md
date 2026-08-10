# PIHC3 collection-membership authoring

Date: 2026-08-02

## Outcome

- Reverified the exact live PIHC3 module tree: it contains no directory named
  `legacy` or `inactive_modules`, no `_asset_component` path, and no directory
  ending in `_component`, including empty directories.
- Reverified all 847 remaining `.paradev/meta.yaml` files. Every file contains
  exactly one real `collection` assignment: 738 Focus members and 109 Modifier
  members. They are not compiler-setting leftovers or user-maintained module
  definitions.
- Added one guarded `Project.set_module_collection(...)` operation. It plans by
  default, requires the exact plan hash to apply, detects unrelated metadata
  changes, validates same-family/same-source-root ownership, migrates old
  visible collection keys, preserves unrelated hidden settings, and removes an
  empty hidden metadata directory when membership is cleared.
- Exposed that operation consistently through `module-collection-set`, REST,
  MCP, the desktop Python bridge, Tauri, and the generated frontend contract.
- Added a Collection picker to the ordinary module Info panel. Users and agents
  select a collection or “No collection”; they never edit hidden metadata.
- Hardened the desktop bridge to validate the complete request before opening a
  project, and hardened the TypeScript service to reject inconsistent dry/apply
  states, project roots, and plan hashes before refreshing the GUI.
- Collection rename now fails closed while members still reference the old id,
  with an actionable instruction to reassign or clear them first. This removes
  the former dangling-reference failure mode until member rewrites can join the
  durable directory-rename recovery journal atomically.

## Verification

- Maintained Python gate: 2,326 passed and nine expected native-Windows-only
  skips.
- Desktop gate: 90 files and 1,465 tests passed.
- Strict TypeScript and Vite production build passed; the existing chunk-size
  warning remains informational.
- Rust `cargo check` passed.
- Black and Flake8 repository gates passed.
- Isolated strict PIHC3 plans:
  - full and cached: 14,617 modules, 106 collections, 35,131 artifacts;
  - Focus family: 738 modules, 28 collections, 12,499 artifacts;
  - `FOCUS_C01_C02_EVERFREE_FIELDTRIP`: 83 modules, one collection, 11,161
    artifacts.
- Every compilation mode reported zero diagnostics, zero errors, and
  `blocked: false`.

## Next

- Completed in [PIHC3 Atomic Collection Rename](2026-08-02-pihc3-atomic-collection-rename.md):
  descriptor moves and explicit member references now share the same durable
  source-draft transaction. Continue simplifying the collection-versus-module
  authoring vocabulary without reintroducing visible metadata maintenance.
