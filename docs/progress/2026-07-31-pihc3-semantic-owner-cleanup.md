# PIHC3 semantic-owner cleanup

Date: 2026-07-31

## Outcome

- Removed the four transitional `decision_support`, `idea_support`,
  `special_project_support`, and `technology_support` source and extension
  families.
- Moved their five resource-set modules into `decision`, `idea`,
  `special_project`, and `technology`. The module object ids and game-shaped
  source paths remain stable; only the semantic owner family changed.
- Extended each project-local HeavenBase Entity with explicit shared PDX or
  asset resource slots. The owning compiler validates authored node modules
  separately while emitting shared files at their checked-in game paths.
- Removed all PIHC3 `meta.publication.replaces_families` tombstones and all
  retired `_component` / `_asset_component` vocabulary from live project
  extensions.
- Renamed 60 generated MIO localization files one-for-one to remove
  `COMPONENT` from their filenames. Localization payloads and the 35,139-file
  output cardinality are unchanged.
- Kept four gameplay modules whose object ids contain `LEGACY`; they are active
  semantic game content, not migration folders or alternate source roots.

## Guardrails

- The whole-tree hygiene test rejects exact `legacy/`, `inactive_modules/`,
  transitional support-family, `_component`, and `_asset_component`
  directories.
- The direct-unit naming test also rejects `component` and `asset_component`
  tokens in the machine-id segment before ` - <title>`, so readable suffixes
  cannot hide a retired component identity.
- It also rejects component-family or `replaces_families` vocabulary in PIHC3
  extension Python and Registry descriptors.
- A dedicated module-partial regression proves the asset-only
  `idea/HOI4_LAW_ICONS` resource set still emits all 17 DDS overrides.
- Technology tests prove shared source files live under the owner family,
  remain independently editable, and retain strict PDX syntax diagnostics.

## Verification

- Consolidation and migration contracts: 165 passed after expectation updates.
- Owner-family regressions: 13 passed.
- Complete Python gate: 2,356 passed, with nine native-Windows tests skipped.
- Isolated clean and cached builds: 14,617 active modules, 106 collections,
  35,139 artifacts, zero diagnostics or errors.
- Idea family partial: 392 modules, 12,187 artifacts, zero diagnostics.
- Idea asset-only module partial: one module, zero diagnostics.
- Technology shared-resource module partial: one module, both shared PDX files
  present, zero diagnostics.
- Focus collection partial: 83 modules, one collection, 11,161 artifacts, zero
  diagnostics.
- Final live-tree audit: 14,708 direct source units, zero forbidden
  directories, zero component-token object ids, zero malformed titled folders,
  zero non-minimal visible metadata files, and zero source symlinks.
- Focused cleanup/consolidation suite after the strengthened guard: 38 passed.
- Post-partial output closure: 35,139 files.
