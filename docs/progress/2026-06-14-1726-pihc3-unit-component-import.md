# PIHC3 Unit Component Progress

Date: 2026-06-14 17:26

Linear: none

## Done

- Added the `unit_component` simple-source family with one path-preserving PDX slot.
- Added `migrate_pihc2_unit_components.py` for the 25 remaining compiled `common/units` support files.
- Imported root unit definitions, convoy/train/ship-hull support files, and unit modifier support into `src/modules/unit_component/`.
- Excluded the reviewed paths from the PIHC_dev copy overlay while keeping equipment, designer modules, division names, codenames, and upgrades with their existing native owners.
- Updated migration docs and central legacy inventory.

## Verification

- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k unit_component`
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_unit_components.py --clean`
- `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-unit-component-build.json`
- Build summary: 16,513 modules, 62 collections, 36,216 artifacts, 1,857 warnings, 0 errors, `blocked: false`.
- Ownership check: all 25 reviewed unit/equipment support paths are `unit_component` owned, with 0 copy-owned and 0 missing.

## Risks Or Blockers

- The slice preserves compiled support files path-by-path; it does not create editable sub-unit or ship-hull schemas.
- Full gameplay parity still needs later balancing and GUI authoring review if these low-level records become user-editable.

## Next

- Continue with another non-map copy-owned domain such as scripted localisation, aggregate achievement support, doctrine/technology support, or broader UI/music assets.
