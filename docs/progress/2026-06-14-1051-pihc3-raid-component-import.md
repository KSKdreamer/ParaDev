# PIHC3 Raid Component Import

Date: 2026-06-14 10:51 Asia/Shanghai

## Summary

- Added `projects/PIHC3/scripts/migrate_pihc2_raid_components.py` to import compiled PIHC_dev raid support files.
- Added the project-local `raid_component` family with a generic path-preserving PDX slot.
- Regenerated 4 `src/modules/raid_component` modules:
  - 3 `common/raids/*.txt` raid type files;
  - 1 `common/raids/categories/*.txt` category file.
- Excluded those reviewed raid support paths from the PIHC_dev copy overlay.
- Updated the raid migration note, copy-overlay baseline, main migration design, and legacy inventory.

## Verification

- Red check before implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'raid_component'` failed on the missing `raid_component` family and missing `projects/PIHC3/scripts/migrate_pihc2_raid_components.py`.
- Focused green after implementation: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'raid_component'` passed `2 passed, 72 deselected`.
- Formatting/style: `rtk uv run black tests/test_pihc3_migration_contracts.py projects/PIHC3/scripts/migrate_pihc2_raid_components.py` and `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_pihc3_migration_contracts.py projects/PIHC3/scripts/migrate_pihc2_raid_components.py` completed cleanly.
- Importer run: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_raid_components.py --clean` imported 4 modules.
- Full PIHC3 emit build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json` completed with 12,037 modules, 62 collections, 36,214 artifacts, 3,842 diagnostics, 0 errors, and `blocked: false`.
- Manifest check found 4 raid-component modules, 4 raid-component-owned artifacts, and 0 build errors.

## Notes

- The importer preserves compiled PIHC_dev raid files exactly as game-relative PDX sources instead of splitting raid type or category records.
- The reviewed files include current-format raid definitions for air, nuclear, and paratrooper raids plus the category table.
- Higher-level editable raid type/category authoring and Gotterdammerung gameplay validation remain future work.
