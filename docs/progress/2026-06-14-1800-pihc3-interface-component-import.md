# PIHC3 Interface Component Progress

Date: 2026-06-14 18:00 CST

Linear: none

## Done

- Added the `interface_component` simple-source family with one shared path-preserving copy slot.
- Added `migrate_pihc2_interface_components.py` for 671 reviewed compiled root/interface GUI/GFX and `gfx/interface` texture files.
- Imported remaining interface support into one aggregate module at `src/modules/interface_component/INTERFACE_COMPONENT_PIHC_INTERFACE/`.
- Excluded reviewed `interface/**/*.gfx`, `interface/**/*.gui`, `gfx/interface/**/*.dds`, and `gfx/interface/**/*.tga` paths from the PIHC_dev copy overlay.
- Kept already-native specialized roots out of the importer, including decision, technology, focus, event, portrait, idea, intelligence-agency, BOP, special-project, compact-UI, texticon, inventory-item, equipment, equipment-module, modifier, bookmark, and equipment-designer support assets.
- Updated migration docs and central legacy inventory.

## Verification

- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k interface_component`
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_interface_components.py --clean`
- `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-interface-component-build.json`
- Build summary: 16,544 modules, 62 collections, 36,216 artifacts, 1,857 warnings, 0 errors, `blocked: false`.
- Ownership check: all 671 reviewed interface support paths are `interface_component` owned, with 0 copy-owned and 0 missing.

## Risks Or Blockers

- The slice preserves compiled GUI/GFX and texture files byte-for-byte; it does not create editable GUI or sprite schemas.
- Non-game metadata and local helper files such as `.DS_Store` and `gfx/interface/techtree/script.py` remain outside the reviewed source set.

## Next

- Continue with another non-map copy-owned domain such as localization overlay cleanup, common doctrine/terrain/weather support, or remaining DLC/common support files.
