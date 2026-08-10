# 2026-06-16 10:19 PIHC3 character native metadata

## Scope

Continued the non-map PIHC2 to PIHC3 migration by enriching native `character` metadata. The family still keeps one editable character module per PIHC2 `resources/characters/<TAG>` folder, using existing `def`, `loc`, and `portrait` source slots.

## Changes

- Added a red metadata contract for generated native character `meta.yaml` settings.
- Added importer metadata for character ids, compiled-character status, source file counts, source slot counts, PIHC2 source evidence, `info.json` keys, localization languages and keys, role field keys, role traits, role description keys, ideology keys, advisor slots, portrait reference counts, portrait roles, portrait variants, compiled portrait paths, and native PNG portrait dimensions/byte sizes.
- Moved legacy source copying before metadata generation so `legacy_resource_source` reflects the files present in each module.
- Regenerated all 250 native character modules under `projects/PIHC3/src/modules/character/`.
- Updated the character migration note, PIHC3 design summary, and legacy inventory.

## Evidence

- Red contract: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k character_importer_extracts_source_slot_and_portrait_metadata_contract` failed with `KeyError: 'character_id'`.
- Green focused contract before regeneration: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k character_importer_extracts_source_slot_and_portrait_metadata_contract` passed with 1 test and 224 deselected.
- Regeneration: `Imported 250 PIHC2 character modules into /Users/magolor/Utils/ParaDev-3/projects/PIHC3/src/modules/character`.
- Metadata coverage: 250 native character modules now have 35-40 settings keys each, averaging 38.1. All 250 modules carry `native_portrait` metadata, and the regenerated set records 839 legacy source evidence paths.
- Role coverage: 129 advisors, 41 corps commanders, 115 country leaders, and 12 field marshals are summarized in metadata.
- Formatting: `rtk uv run black projects/PIHC3/scripts/migrate_pihc2_characters.py tests/test_pihc3_migration_contracts.py` left both files unchanged.
- Green focused group after regeneration: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k character_importer` passed with 2 tests and 223 deselected.
- Black check: `rtk uv run black --check projects/PIHC3/scripts/migrate_pihc2_characters.py tests/test_pihc3_migration_contracts.py` passed.
- Heaven-style scan: `OK: 2 file(s) - no banned imports`.
- Build: `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-character-native-metadata-build.json`.
- Build summary: 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, `blocked: false`.
- Build ownership: 750 `module:character/...` artifacts: 250 `common/characters/*.txt` files and 500 localization YAML files, with 0 character-owned `copy_root` artifacts. Module-local `portrait.png` remains source data for GUI browsing and future generation work, not an emitted artifact.

## Follow-Up

Portrait DDS regeneration from source images, animation strip handling, role-specific authoring helpers, editable random-character pool reconstruction, and dedicated gameplay parity review remain future slices.
