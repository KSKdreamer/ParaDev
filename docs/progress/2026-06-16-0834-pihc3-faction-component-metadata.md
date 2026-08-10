# 2026-06-16 08:34 PIHC3 faction component metadata

## Scope

Continued the non-map PIHC2 to PIHC3 migration by enriching the `faction_component` importer for compiled faction goals, manifests, icon pools, rules, rule groups, upgrades, and member upgrades. The family still uses shared path-preserving PDX and loc slots; the new data lives in generic `meta.yaml` settings for GUI browsing.

## Changes

- Added a red metadata contract for generated faction-component `meta.yaml` settings.
- Updated the existing family slot contract to match current `paradev.yaml`: `faction_component` now has a generic optional loc slot and localization output template.
- Added importer metadata for component id/domain, source size, root and wrapper keys, inferred wrapper records, record ids, first/last record samples, direct field-key counts, scalar/block/bare field counts, scalar field values, block-field root-key counts, localization languages, and localization keys.
- Regenerated the 19 `faction_component` modules under `projects/PIHC3/src/modules/faction_component/`.
- Updated the factions migration note, PIHC3 design summary, and legacy inventory.

## Evidence

- Red contract: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k faction_component_importer_extracts_metadata_contract` failed with `KeyError: 'component_id'`.
- Green focused contract before formatting: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k faction_component_importer_extracts_metadata_contract` passed with 1 test and 217 deselected.
- Regeneration: `Imported 19 PIHC2 faction component modules into /Users/magolor/Utils/ParaDev-3/projects/PIHC3/src/modules/faction_component`.
- Metadata coverage: 19 faction-component modules now have 28 settings keys each.
- Formatting: `rtk uv run black projects/PIHC3/scripts/migrate_pihc2_faction_components.py tests/test_pihc3_migration_contracts.py` reformatted 2 files.
- Green focused group after formatting and slot-contract update: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k faction_component` passed with 3 tests and 215 deselected.
- Black check: `rtk uv run black --check projects/PIHC3/scripts/migrate_pihc2_faction_components.py tests/test_pihc3_migration_contracts.py` passed.
- Heaven-style scan: `OK: 2 file(s) - no banned imports`.
- Build: `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json`.
- Build summary: 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, `blocked: false`.
- Build ownership: 49 `module:faction_component/...` artifacts, including 19 reviewed PDX support files and 30 generated localization files; 0 reviewed non-template `common/factions/` paths are copy-root owned.

## Follow-Up

Higher-level editable faction goal, manifest, rule, upgrade, member-upgrade, and icon-pool authoring remains future work. The current slice preserves compiled support files and exposes enough generic metadata for browsing without adding subsystem-specific module families.
