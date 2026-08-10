# 2026-06-16 09:15 PIHC3 technology asset metadata

## Scope

Continued the non-map PIHC2 to PIHC3 migration by enriching `technology_asset_component` metadata. The family still uses one shared path-preserving copy slot for compiled technology GFX/DDS assets, and PIHC2 `default.png` files remain non-emitted legacy evidence.

## Changes

- Added a red metadata contract for generated technology-asset-component `meta.yaml` settings.
- Added importer metadata for component ids, source file counts, source slot counts, GFX/DDS source counts, sprite names, texture paths, optional frame counts, DDS dimensions, mipmaps, byte sizes, FourCC values, header sizes, and per-file GFX/DDS summaries.
- Preserved the existing PIHC2 `resources/technologies/<TAG>/default.png` legacy evidence fields.
- Regenerated all 305 `technology_asset_component` modules under `projects/PIHC3/src/modules/technology_asset_component/`.
- Updated the technology asset migration note, PIHC3 design summary, and legacy inventory.

## Evidence

- Red contract: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k technology_asset_component_importer_extracts_metadata_contract` failed with `KeyError: 'component_id'`.
- Green focused contract before regeneration: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k technology_asset_component_importer_extracts_metadata_contract` passed with 1 test and 220 deselected.
- Regeneration: `Imported 305 PIHC2 technology asset component modules into /Users/magolor/Utils/ParaDev-3/projects/PIHC3/src/modules/technology_asset_component`.
- Metadata coverage: 305 technology-asset-component modules now have 18-20 settings keys each; the regenerated set has 300 paired GFX/DDS modules and 5 DDS-only support-icon modules.
- Formatting: `rtk uv run black projects/PIHC3/scripts/migrate_pihc2_technology_asset_components.py tests/test_pihc3_migration_contracts.py` reformatted the test file; the importer was already formatted.
- Green focused group after regeneration: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k technology_asset_component` passed with 3 tests and 218 deselected.
- Black check: `rtk uv run black --check projects/PIHC3/scripts/migrate_pihc2_technology_asset_components.py tests/test_pihc3_migration_contracts.py` passed.
- Heaven-style scan: `OK: 2 file(s) - no banned imports`.
- Build: `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json`.
- Build summary: 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, `blocked: false`.
- Build ownership: 605 `module:technology_asset_component/...` copy artifacts. All 605 reviewed `interface/technologies/*.gfx` and `gfx/interface/technologies/*.dds` artifacts are owned by `technology_asset_component`, with 0 copy-root-owned reviewed technology asset paths.

## Follow-Up

Focus asset components still have similarly sparse metadata and should receive the same generic GFX/DDS summary treatment in a later slice. Technology root GUI fragments, equipment/module side-effect review, doctrine coordination, source-image regeneration, and parity review against `PIHC_dev` remain future technology work.
