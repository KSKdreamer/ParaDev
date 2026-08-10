# PIHC3 MIO trait node authoring

Date: 2026-07-31

## Outcome

- Added a registry-owned `ModuleDiagramNodeAuthoring` form contract and paired
  `ModuleDiagramNodePlanner`; a graph provider now owns both discovery and
  mutation semantics.
- The shared HoI4 MIO provider exposes **Add graph item** for an editable
  selected trait. It creates a child trait inside the same organization,
  reviews the exact PDX and localization replacements, and returns the created
  organization/node ids for renderer reconciliation.
- The PIHC3 MIO extension continues to own its Entity, source slots, and
  compiler while atomically replacing the profile provider through the
  registry. It contains no duplicate insertion implementation.
- SDK, frontend contract, CLI, REST, MCP, Python desktop bridge, Rust desktop
  command, and React use the same bounded `node_intents` request. Node creation
  cannot be mixed with movement/edge edits and Apply requires the exact dry
  plan hash.
- The generic desktop dialog renders provider-declared fields, keeps selected
  source/revision context hidden, invalidates review on edits, and applies one
  guarded transaction. Its review exposes the exact replacement ranges,
  inserted PDX/localization text, and plan hash. There is no MIO grammar or
  localization logic in TypeScript.
- Public build API and generated references now contain 121 symbols.
- The active MIO provider now exposes only the clean public selectors
  `military_industrial_organization` and `mio`; the retired
  `_component` selector is no longer published or normalized by the desktop.

## PIHC3 source audit

- Recursive audit: zero `_component`, `_asset_component`, `legacy`,
  `inactive_modules`, or `__pycache__` directories.
- All 14,618 direct family module/collection folders use the canonical
  `id - preferred localization` physical name.
- The real PIHC3 MIO node dry plan reviewed exactly one organization definition
  and its localization file. No real project source was written.
- Strict full PIHC3 plan: 14,617 modules, 106 collections, 35,139 artifacts,
  zero diagnostics.
- MIO family plan: 7 modules, 11,001 artifacts, zero diagnostics.

## Safety contract

- The planner verifies the selected organization, parent trait, source path,
  source revision, localization ownership, language, field values, and id/key
  uniqueness.
- It reparses generated PDX, creates canonical localization, and emits exact
  source replacements under the existing crash-safe diagram transaction.
- Family build acceptance and HeavenBase Catalog refresh remain mandatory
  before backups are discarded.

## Regression gates

- Python: 2,172 passed; nine native-Windows tests skipped.
- Desktop: all 87 files and 1,415 tests passed.
- Rust/Tauri: all 93 unit tests passed.
- TypeScript/Vite production build and focused changed-source lint passed.
- Main and nested PIHC3 repository diff-integrity checks passed.
