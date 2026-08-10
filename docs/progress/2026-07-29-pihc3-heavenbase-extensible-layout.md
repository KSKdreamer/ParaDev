# PIHC3 HeavenBase Extensible Layout

Date: 2026-07-29

PIHC3 now uses one semantic source tree and one HeavenBase 0.1.2.1 Registry
extension model.

## Source layout

- Removed every `legacy/`, `_asset_component`, and `inactive_modules/` source
  directory.
- Integrated definitions, localization, previews, icons, DDS/GFX, and other
  resources into the semantic module that owns them.
- Normalized all 14,708 module/collection source folders to
  `<object id> - <preferred-language title>` while preserving logical IDs and
  Windows archive path budgets.
- Kept visible per-module metadata to `collection`, `inactive`, or `comment`.
  Folder-derived titles, importer provenance, compiler defaults, and graph
  state live under the hidden module-local `.paradev/` directory when needed.
- Replaced the aggregate `focus_tree` source family with 28 focus collections
  and 738 independently editable focus modules.

## Registry architecture

- PIHC3 has 76 standalone project extension folders discovered by convention;
  `paradev.yaml` no longer maintains a central Python/family import list.
- All 75 module-type extensions register a concrete project-local `hb.Entity`
  class with its family identity, resource slots, and
  `normalize`/`check`/`emit` compilation hooks.
- The `localisation` extension is intentionally an artifact postprocessor, not
  a module Entity.
- PIHC3-exclusive `inventory_item`, `state_lore`, `superevent`, and generic
  project `entity` contracts are defined and registered inside PIHC3.
- Core semantic families use concrete project-owned family classes. Hidden
  low-level HoI4 file-domain families retain declarative compiler definitions
  but now use the same concrete Entity/Extension Registry lifecycle.

## Authoring contract

- All 51 PIHC3 project templates create
  `<object id> - <preferred-language title>` folders.
- Forty-eight templates create no visible metadata. Decision and focus
  templates keep only `collection`; the empty portrait shell keeps only an
  author-facing `comment`.
- Five templates with compiler defaults use the new trusted `system_files`
  channel to write `.paradev/meta.yaml` in the same crash-safe scaffold
  transaction. Project templates still cannot place `.paradev/` paths in
  ordinary author files.
- Focus, technology, doctrine, and MIO graph sources are editable through the
  shared module-diagram SDK/desktop path.

## Verification

- Static gate: `scripts/flake.bash --ci` passed before the final template slice.
- Final Python fast gate: 2,260 passed, 10 expected platform/fixture skips.
- Desktop tests: 1,405 passed across 85 files.
- Desktop production build: TypeScript and Vite passed.
- Current template/layout focused gate: 29 passed.
- Direct PIHC3 dry plans:
  - clean/full: 14,617 modules, 106 collections, 35,138 artifacts, 0 errors;
  - cached/full: identical;
  - focus family: 738 modules, 28 collections, 12,499 artifacts, 0 errors;
  - technology family: 300 modules, 11,899 artifacts, 0 errors;
  - MIO family: 7 modules, 11,001 artifacts, 0 errors;
  - one technology module: 1 module, 10,997 safe-scope artifacts, 0 errors.
- Isolated real publication:
  - clean/full, cached/full, focus-family partial, and one-technology partial
    all emitted with `dry_run: false` and zero errors;
  - final isolated output contained 35,138 files / 1,221,764,608 bytes plus the
    summary manifest and emitted-artifact ownership ledger;
  - the temporary output was removed after verification and no game directory
    was touched.

## Follow-up

- The first PIHC3 publication spends roughly 90-100 seconds validating and
  hashing before completion. Emit an earlier `validating_publication` progress
  event so the GUI never appears idle during this data-safety phase.
- Python's default macOS temporary path passes through the `/var` symlink and
  is rejected by the anchored publication guard. Normal project paths are
  unaffected. A later compatibility slice should canonicalize trusted
  temporary roots or present a specific actionable path error without
  weakening symlink protections.
- The 24 hidden low-level file-domain families are no longer asset sidecars,
  but further semantic consolidation can retire names such as
  `*_component` where a clear owning module exists.
