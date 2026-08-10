# 2026-06-16 10:49 PIHC3 idea native metadata

## Scope

Continued the non-map PIHC2 to PIHC3 migration by enriching native `idea` metadata. The family still keeps one editable idea module per PIHC2 `resources/ideas/<TAG>` folder and uses existing shared `def`, localization, and optional icon slots; source images remain non-emitted legacy evidence in this slice.

## Changes

- Added a red metadata contract for generated native idea source-slot, localization, field-summary, and source-image settings.
- Added importer metadata for idea ids, legacy output paths, source slot counts, PIHC2 source evidence, `info.json` keys, localization languages and keys, shallow scalar/block/list field summaries, modifier field names, trigger block names, and legacy source-image PNG dimensions/byte sizes when available.
- Regenerated all 390 native idea modules under `projects/PIHC3/src/modules/idea/`.
- Updated the idea migration note, PIHC3 design summary, and legacy inventory.

## Evidence

- Red contract: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k idea_importer_extracts_source_slot_localization_and_image_metadata_contract` failed with `KeyError: 'idea_id'`.
- Green focused contract before regeneration: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k idea_importer_extracts_source_slot_localization_and_image_metadata_contract` passed with 1 test and 226 deselected.
- Regeneration: `Imported 390 PIHC2 idea modules into /Users/magolor/Utils/ParaDev-3/projects/PIHC3/src/modules/idea`.
- Metadata coverage: 390 native idea modules now have 32-46 settings keys each, averaging 35.7. All 390 modules carry localization metadata, 341 expose modifier-field summaries, 390 expose trigger-block summaries, 292 record legacy source-image metadata, and the regenerated set records 1,070 legacy source evidence paths.
- Formatting: `rtk uv run black projects/PIHC3/scripts/import_pihc2_ideas_current.py tests/test_pihc3_migration_contracts.py` left both files unchanged.
- Green focused group after regeneration: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k idea_importer` passed with 2 tests and 225 deselected.
- Black check: `rtk uv run black --check projects/PIHC3/scripts/import_pihc2_ideas_current.py tests/test_pihc3_migration_contracts.py` passed.
- Heaven-style scan: `OK: 2 file(s) - no banned imports`.
- Build: `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-idea-native-metadata-build.json`.
- Build summary: 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, `blocked: false`.
- Build ownership: 1,166 `module:idea/...` artifacts: 390 `common/ideas/*.txt` files and 776 localization YAML files, with 0 idea-owned `copy_root` artifacts and 0 native idea image artifacts.

## Follow-Up

Source-image-to-DDS icon regeneration remains future work; compiled idea sprites/icons are still preserved by `idea_asset_component`. Nested idea-category law aggregation remains owned by `idea_category`.
