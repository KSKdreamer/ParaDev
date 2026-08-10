# PIHC3 Common Component Import

Date: 2026-06-14 11:26 Asia/Shanghai

## Summary

- Added `projects/PIHC3/scripts/migrate_pihc2_common_components.py` to import compiled PIHC_dev miscellaneous common support files.
- Added the project-local `common_component` family with a generic path-preserving PDX slot.
- Regenerated 12 `src/modules/common_component` modules:
  - 1 `common/abilities/*.txt` file;
  - 2 `common/collections/*.txt` files;
  - 1 `common/scripted_diplomatic_actions/*.txt` file;
  - 1 `common/technology_sharing/*.txt` file;
  - 1 `common/technology_tags/*.txt` file;
  - 1 `common/unit_tags/*.txt` file;
  - 3 `common/units/equipment/upgrades/*.txt` files;
  - 1 `common/units/names/*.txt` file;
  - 1 `common/units/names_railway_guns/*.txt` file.
- Excluded those reviewed support paths from the PIHC_dev copy overlay.
- Updated the common-component migration note, copy-overlay baseline, main migration design, and legacy inventory.

## Verification

- Red check before implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'common_component'` failed on the missing `common_component` family and missing `projects/PIHC3/scripts/migrate_pihc2_common_components.py`.
- Focused green after implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'common_component'` passed `2 passed, 76 deselected`.
- Formatting/style: `rtk uv run black tests/test_pihc3_migration_contracts.py projects/PIHC3/scripts/migrate_pihc2_common_components.py` and `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_pihc3_migration_contracts.py projects/PIHC3/scripts/migrate_pihc2_common_components.py` completed cleanly.
- Importer run: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_common_components.py --clean` imported 12 modules.
- Full PIHC3 emit build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json` completed with 12,080 modules, 62 collections, 36,214 artifacts, 3,842 diagnostics, 0 errors, and `blocked: false`.
- Manifest check found 12 common-component modules, 12 common-component-owned artifacts, and 0 build errors.

## Notes

- The importer preserves compiled PIHC_dev support files exactly as game-relative PDX sources instead of splitting records into editable objects.
- Empty roots such as `common/units/names_ships` are intentionally skipped.
- Higher-level editable authoring for these miscellaneous support domains remains future work only where it proves useful.
