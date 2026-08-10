# 2026-06-16 10:38 PIHC3 trait native metadata

## Scope

Continued the non-map PIHC2 to PIHC3 migration by enriching native `trait` metadata. The family still keeps one editable country-leader trait module per PIHC2 `resources/traits/<TAG>` folder and uses the existing routed `def`, shared localization, and optional icon slots.

## Changes

- Added a red metadata contract for generated native trait source-slot and localization settings.
- Added importer metadata for trait ids, legacy output paths, source slot counts, PIHC2 source evidence, `info.json` keys, localization languages and keys, shallow scalar/block/list field summaries, modifier field names, `ai_will_do` factors, and custom modifier tooltip keys.
- Regenerated all 139 native trait modules under `projects/PIHC3/src/modules/trait/`.
- Updated the trait migration note, PIHC3 design summary, and legacy inventory.

## Evidence

- Red contract: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k trait_importer_extracts_source_slot_and_localization_metadata_contract` failed with `KeyError: 'trait_id'`.
- Green focused contract before regeneration: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k trait_importer_extracts_source_slot_and_localization_metadata_contract` passed with 1 test and 225 deselected.
- Regeneration: `Imported 139 PIHC2 trait modules into /Users/magolor/Utils/ParaDev-3/projects/PIHC3/src/modules/trait`.
- Metadata coverage: 139 native trait modules now have 28-39 settings keys each, averaging 29.6. All 139 modules carry localization metadata, 136 expose modifier-field summaries, 6 record custom tooltip keys, and the regenerated set records 278 legacy source evidence paths.
- Formatting: `rtk uv run black projects/PIHC3/scripts/migrate_pihc2_traits.py tests/test_pihc3_migration_contracts.py` left both files unchanged.
- Green focused group after regeneration: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k trait_importer` passed with 2 tests and 224 deselected.
- Black check: `rtk uv run black --check projects/PIHC3/scripts/migrate_pihc2_traits.py tests/test_pihc3_migration_contracts.py` passed.
- Heaven-style scan: `OK: 2 file(s) - no banned imports`.
- Build: `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-trait-native-metadata-build.json`.
- Build summary: 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, `blocked: false`.
- Build ownership: 417 `module:trait/...` artifacts: 139 `common/country_leader/*.txt` files and 278 localization YAML files, with 0 trait-owned `copy_root` artifacts.

## Follow-Up

Structured unit-leader and scientist trait authoring remains separate from the current country-leader trait importer. Trait icon/image handling remains limited to the shared optional slot because current PIHC2 trait folders contain only `info.json` and `locs.txt`.
