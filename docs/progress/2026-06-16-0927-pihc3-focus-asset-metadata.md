# 2026-06-16 09:27 PIHC3 focus asset metadata

## Scope

Continued the non-map PIHC2 to PIHC3 migration by enriching `focus_asset_component` metadata. The family still uses one shared path-preserving copy slot for compiled focus GFX/DDS assets, and PIHC2 `default.png` files remain non-emitted legacy evidence.

## Changes

- Added a red metadata contract for generated focus-asset-component `meta.yaml` settings.
- Added importer metadata for component ids, source file counts, source slot counts, GFX/DDS source counts, sprite names, texture paths, optional frame counts, DDS dimensions, mipmaps, byte sizes, FourCC values, header sizes, and per-file GFX/DDS summaries.
- Preserved the existing PIHC2 `resources/focuses/<TREE>/<TAG>/default.png` legacy evidence fields.
- Regenerated all 739 `focus_asset_component` modules under `projects/PIHC3/src/modules/focus_asset_component/`.
- Updated the focuses migration note, PIHC3 design summary, and legacy inventory.

## Evidence

- Red contract: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k focus_asset_component_importer_extracts_metadata_contract` failed with `KeyError: 'component_id'`.
- Green focused contract before regeneration: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k focus_asset_component_importer_extracts_metadata_contract` passed with 1 test and 221 deselected.
- Regeneration: `Imported 739 PIHC2 focus asset component modules into /Users/magolor/Utils/ParaDev-3/projects/PIHC3/src/modules/focus_asset_component`.
- Metadata coverage: 739 focus-asset-component modules now have 18-20 settings keys each; the regenerated set has 738 paired GFX/DDS modules and one DDS-only support-icon module.
- Formatting: `rtk uv run black projects/PIHC3/scripts/migrate_pihc2_focus_asset_components.py tests/test_pihc3_migration_contracts.py` reformatted the test file; the importer was already formatted.
- Green focused group after regeneration: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k focus_asset_component` passed with 3 tests and 219 deselected.
- Black check: `rtk uv run black --check projects/PIHC3/scripts/migrate_pihc2_focus_asset_components.py tests/test_pihc3_migration_contracts.py` passed.
- Heaven-style scan: `OK: 2 file(s) - no banned imports`.
- Build: `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json`.
- Build summary: 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, `blocked: false`.
- Build ownership: 1,477 `module:focus_asset_component/...` copy artifacts. All 1,477 reviewed `interface/focuses/*.gfx` and `gfx/interface/goals/*.dds` artifacts are owned by `focus_asset_component`, with 0 copy-root-owned reviewed focus asset paths.

## Follow-Up

Focus-tree per-node editable reconstruction, GUI-first layout review, exact no-focus guard mutation policy, source-image regeneration, and parity review against `PIHC_dev` remain future focus work.
